from __future__ import annotations

from collections.abc import Sequence

from app.modules.dashboard.repository import QuotaObservation
from app.modules.dashboard.schemas import QuotaLbShareEstimate

MIN_REFERENCE_USED_POINTS = 20.0
RESET_DEADLINE_ADVANCE_SECONDS = 86400


def observed_quota_growth(rows: Sequence[QuotaObservation]) -> float:
    """Count new high-water usage within each weekly cycle, including resets."""
    if not rows:
        return 0.0
    high_water = rows[0].used_percent
    previous_reset_at = rows[0].reset_at
    growth = 0.0
    for row in rows[1:]:
        is_reset = (
            row.used_percent < high_water
            and row.reset_at is not None
            and previous_reset_at is not None
            and row.reset_at > previous_reset_at + RESET_DEADLINE_ADVANCE_SECONDS
        )
        if is_reset:
            high_water = row.used_percent
        elif row.used_percent > high_water:
            growth += row.used_percent - high_water
            high_water = row.used_percent
        if row.reset_at is not None:
            previous_reset_at = row.reset_at
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
    last_full_index = next(
        (index for index in range(len(target_rows) - 1, -1, -1) if target_rows[index].used_percent >= 100),
        None,
    )
    if last_full_index is None:
        return None
    since = target_rows[last_full_index].recorded_at
    target_segment = target_rows[last_full_index:]
    observed_points = observed_quota_growth(target_segment)
    if observed_points <= 0:
        return None

    reference_credits = 0.0
    reference_cost = 0.0
    reference_count = 0
    for reference_id, rows in reference_rows.items():
        segment = [row for row in rows if since <= row.recorded_at <= target_segment[-1].recorded_at]
        points = observed_quota_growth(segment)
        cost = costs_by_account.get(reference_id, 0.0)
        if points < MIN_REFERENCE_USED_POINTS or cost <= 0:
            continue
        reference_credits += points * reference_capacities[reference_id] / 100
        reference_cost += cost
        reference_count += 1
    if reference_count < 2 or reference_credits <= 0:
        return None

    target_cost = costs_by_account.get(account_id, 0.0)
    observed_credits = observed_points * target_capacity_credits / 100
    cost_per_credit = reference_cost / reference_credits
    lb_credits = target_cost / cost_per_credit
    lb_points = 100 * lb_credits / target_capacity_credits
    if lb_credits > observed_credits:
        return None
    return QuotaLbShareEstimate(
        account_id=account_id,
        since=since,
        as_of=target_segment[-1].recorded_at,
        window_minutes=window_minutes,
        observed_used_percent=observed_points,
        observed_used_credits=observed_credits,
        estimated_lb_used_credits=lb_credits,
        estimated_lb_used_percent=lb_points,
        estimated_lb_share_percent=100 * lb_points / observed_points,
        reference_account_count=reference_count,
    )
