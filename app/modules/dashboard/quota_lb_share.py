from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone

from app.core.utils.time import naive_utc_to_epoch
from app.modules.dashboard.repository import QuotaObservation
from app.modules.dashboard.schemas import QuotaLbShareEstimate

RESET_DEADLINE_ADVANCE_SECONDS = 86400
RESET_DEADLINE_JITTER_SECONDS = 5


@dataclass(frozen=True)
class _QuotaCycle:
    since: datetime
    reset_at: int | None


def _deadline(value: int) -> datetime:
    return datetime.fromtimestamp(value, timezone.utc).replace(tzinfo=None)


def _expired(row: QuotaObservation) -> bool:
    return row.reset_at is not None and row.reset_at <= naive_utc_to_epoch(row.recorded_at)


def _regressed(previous: QuotaObservation, row: QuotaObservation, cycle_deadline: int | None = None) -> bool:
    return row.reset_at is not None and (
        (previous.reset_at is not None and previous.reset_at > row.reset_at + RESET_DEADLINE_ADVANCE_SECONDS)
        or (cycle_deadline is not None and row.reset_at < cycle_deadline - RESET_DEADLINE_JITTER_SECONDS)
    )


def _is_reset(previous: QuotaObservation, row: QuotaObservation, window_minutes: int | None = None) -> bool:
    if row.used_percent == 0 and (previous.used_percent > 1 or (previous.used_percent > 0 and row.reset_at is None)):
        return True
    if row.reset_at is not None and previous.reset_at is not None:
        return (
            row.reset_at >= previous.reset_at + RESET_DEADLINE_ADVANCE_SECONDS
            or (previous.reset_at <= naive_utc_to_epoch(row.recorded_at) < row.reset_at)
            or (
                row.reset_at > previous.reset_at
                and previous.recorded_at
                <= _deadline(row.reset_at) - timedelta(minutes=window_minutes or row.window_minutes)
                <= row.recorded_at
            )
        )
    return False


def current_quota_cycle_start(rows: Sequence[QuotaObservation], window_minutes: int) -> datetime | None:
    """Locate the current cycle without requiring a full or zero usage sample."""
    cycle = _current_quota_cycle(rows, window_minutes)
    return cycle.since if cycle is not None else None


def _current_quota_cycle(rows: Sequence[QuotaObservation], window_minutes: int) -> _QuotaCycle | None:
    if not rows or _expired(rows[-1]):
        return None
    previous: QuotaObservation | None = None
    since: datetime | None = None
    cycle_deadline: int | None = None
    duration = timedelta(minutes=window_minutes)
    for row in rows:
        if previous is not None and previous.reset_at is None and cycle_deadline is not None:
            previous = replace(previous, reset_at=cycle_deadline)
        if previous is not None and _regressed(previous, row, cycle_deadline):
            if row is rows[-1]:
                return None
            continue
        if _expired(row):
            # Expired observations can bracket the next natural reset, but
            # cannot establish a fresh current cycle themselves.
            previous = row
            continue
        inferred = _deadline(row.reset_at) - duration if row.reset_at is not None else row.recorded_at
        if since is None:
            since = min(inferred, row.recorded_at) if row.reset_at is not None or row.used_percent == 0 else None
            cycle_deadline = row.reset_at
        if previous is not None and _is_reset(previous, row, window_minutes):
            if previous.used_percent == 0 and since is not None and since - timedelta(minutes=5) <= inferred <= since:
                # A zero reading may precede its renewed deadline by a poll.
                # Keep that reset's boundary instead of starting it twice.
                since = min(since, inferred)
            elif (
                previous.reset_at is not None
                and previous.recorded_at <= _deadline(previous.reset_at) <= row.recorded_at
            ):
                since = _deadline(previous.reset_at)
            elif previous.recorded_at <= inferred <= row.recorded_at:
                since = inferred
            elif (
                row.reset_at is not None
                and previous.reset_at is not None
                and row.reset_at >= previous.reset_at + RESET_DEADLINE_ADVANCE_SECONDS
                and inferred <= row.recorded_at
            ):
                # Renewed metadata can arrive after a stale old-deadline poll.
                # Its window start still belongs to the fresh cycle.
                since = inferred
            else:
                since = row.recorded_at
            cycle_deadline = row.reset_at
        previous = row
    if cycle_deadline is not None and cycle_deadline <= naive_utc_to_epoch(rows[-1].recorded_at):
        return None
    return _QuotaCycle(since, cycle_deadline) if since is not None else None


def observed_quota_growth(rows: Sequence[QuotaObservation]) -> float:
    """Calibrate growth, counting the entire first reading after each reset."""
    previous: QuotaObservation | None = None
    high_water = growth = 0.0
    cycle_deadline: int | None = None
    for row in rows:
        if previous is not None and previous.reset_at is None and cycle_deadline is not None:
            previous = replace(previous, reset_at=cycle_deadline)
        if previous is not None and _regressed(previous, row, cycle_deadline):
            continue
        if _expired(row):
            previous = row
            continue
        if previous is None:
            high_water = row.used_percent
            cycle_deadline = row.reset_at
        elif _is_reset(previous, row):
            growth += row.used_percent
            high_water = row.used_percent
            cycle_deadline = row.reset_at
        elif row.used_percent > high_water:
            growth += row.used_percent - high_water
            high_water = row.used_percent
        previous = row
    return growth


def estimate_quota_lb_share(
    *,
    account_id: str,
    target_rows: Sequence[QuotaObservation],
    target_capacity_credits: float,
    window_minutes: int,
    reference_rows: dict[str, list[QuotaObservation]],
    reference_capacities: dict[str, float],
    costs_by_account: dict[str, float],
) -> QuotaLbShareEstimate | None:
    cycle = _current_quota_cycle(target_rows, window_minutes)
    if cycle is None:
        return None
    observed_points = target_rows[-1].used_percent
    target_cost = costs_by_account.get(account_id, 0.0)
    if observed_points == 0 and target_cost > 0:
        return None

    reference_credits = reference_cost = 0.0
    reference_count = 0
    for reference_id, rows in reference_rows.items():
        if not rows or _current_quota_cycle(rows, rows[-1].window_minutes) is None:
            continue
        points = rows[-1].used_percent
        cost = costs_by_account.get(reference_id, 0.0)
        if points <= 0 or cost <= 0:
            continue
        reference_credits += points * reference_capacities[reference_id] / 100
        reference_cost += cost
        reference_count += 1
    if reference_credits <= 0 and observed_points > 0 and target_cost > 0:
        return None

    observed_credits = observed_points * target_capacity_credits / 100
    lb_credits = target_cost * reference_credits / reference_cost if reference_cost > 0 else 0.0
    lb_points = 100 * lb_credits / target_capacity_credits
    return QuotaLbShareEstimate(
        account_id=account_id,
        since=cycle.since,
        as_of=target_rows[-1].recorded_at,
        reset_at=_deadline(cycle.reset_at) if cycle.reset_at is not None else None,
        window_minutes=window_minutes,
        observed_used_percent=observed_points,
        observed_used_credits=observed_credits,
        estimated_lb_used_credits=lb_credits,
        estimated_lb_used_percent=lb_points,
        estimated_lb_share_percent=100 * lb_points / observed_points if observed_points > 0 else 0.0,
        reference_account_count=reference_count,
    )
