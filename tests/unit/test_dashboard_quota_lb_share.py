from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.modules.dashboard.quota_lb_share import (
    current_quota_cycle_start,
    estimate_quota_lb_share,
    observed_quota_growth,
)
from app.modules.dashboard.repository import QuotaObservation

BASE = datetime(2026, 9, 22, 9, 0)


def _row(account_id: str, hour: float, used: float, reset_day: float | None) -> QuotaObservation:
    return QuotaObservation(
        account_id=account_id,
        recorded_at=BASE + timedelta(hours=hour),
        used_percent=used,
        reset_at=(
            int((BASE + timedelta(days=reset_day)).replace(tzinfo=timezone.utc).timestamp())
            if reset_day is not None
            else None
        ),
    )


def _estimate(target: list[QuotaObservation], cost: float = 37.8):
    return estimate_quota_lb_share(
        account_id="target",
        target_rows=target,
        target_capacity_credits=7560,
        window_minutes=10080,
        reference_rows={"peer": [_row("peer", 0, 0, 7), _row("peer", 1, 10, 7)]},
        reference_capacities={"peer": 7560},
        costs_by_account={"target": cost, "peer": 7.56},
    )


def test_current_cycle_does_not_accumulate_old_cycles() -> None:
    target = [
        _row("target", 0, 100, 0),
        _row("target", 1, 5, 7),
        _row("target", 100, 55, 7),
        _row("target", 101, 0, 11),
        _row("target", 190, 99, 11),
        _row("target", 191, 0, 15),
        _row("target", 199, 6, 15),
    ]
    estimate = _estimate(target, cost=3.78)
    assert estimate is not None
    assert estimate.observed_used_percent == 6
    assert estimate.observed_used_credits == pytest.approx(453.6)
    assert estimate.since == BASE + timedelta(hours=191)
    assert estimate.estimated_lb_share_percent == pytest.approx(83.333333)


@pytest.mark.parametrize("first_used", [5, 10, 20])
def test_reset_includes_nonzero_equal_and_higher_readings(first_used: float) -> None:
    rows = [_row("target", 0, 0, 7), _row("target", 1, 10, 7), _row("target", 169, first_used, 14)]
    assert observed_quota_growth(rows) == 10 + first_used
    assert current_quota_cycle_start(rows, 10080) == BASE + timedelta(days=7)
    estimate = _estimate(rows)
    assert estimate is not None
    assert estimate.observed_used_percent == first_used


def test_first_five_percent_reading_needs_no_previous_full_sample() -> None:
    estimate = _estimate([_row("target", 1, 5, 7)], cost=1.89)
    assert estimate is not None
    assert estimate.observed_used_percent == 5
    assert estimate.since == BASE
    assert estimate.estimated_lb_share_percent == pytest.approx(50)
    assert estimate.reference_account_count == 1


def test_percentage_above_one_hundred_is_not_hidden() -> None:
    estimate = _estimate([_row("target", 1, 5, 7)], cost=7.56)
    assert estimate is not None
    assert estimate.estimated_lb_share_percent == pytest.approx(200)


def test_same_cycle_corrections_do_not_reset_and_latest_use_is_the_denominator() -> None:
    rows = [_row("target", 0, 30, 7), _row("target", 1, 29, 7), _row("target", 2, 30, 7), _row("target", 3, 35, 7)]
    assert observed_quota_growth(rows) == 5
    assert current_quota_cycle_start(rows, 10080) == BASE
    estimate = _estimate(rows[:-1])
    assert estimate is not None
    assert estimate.observed_used_percent == 30


def test_unused_cycle_reports_zero_without_peer_calibration() -> None:
    estimate = estimate_quota_lb_share(
        account_id="target",
        target_rows=[_row("target", 1, 0, 7)],
        target_capacity_credits=7560,
        window_minutes=10080,
        reference_rows={},
        reference_capacities={},
        costs_by_account={},
    )
    assert estimate is not None
    assert estimate.estimated_lb_share_percent == 0
    assert _estimate([_row("target", 1, 0, 7)], cost=1) is None


@pytest.mark.parametrize("latest", [_row("target", 169, 100, 7), _row("target", 170, 100, 7)])
def test_expired_and_regressed_readings_do_not_restore_old_cycle(latest: QuotaObservation) -> None:
    rows = [_row("target", 0, 90, 7), _row("target", 169, 5, 14), latest]
    assert current_quota_cycle_start(rows, 10080) is None
    assert _estimate(rows) is None


def test_zero_before_deadline_refresh_is_one_reset() -> None:
    rows = [_row("target", 23, 55, 7), _row("target", 24, 0, 7), _row("target", 24.01, 5, 8)]
    assert current_quota_cycle_start(rows, 10080) == BASE + timedelta(days=1)
    assert observed_quota_growth(rows) == 5


def test_reset_without_deadline_metadata() -> None:
    rows = [_row("target", 0, 55, None), _row("target", 1, 0, None), _row("target", 2, 5, None)]
    assert current_quota_cycle_start(rows, 10080) == BASE + timedelta(hours=1)
    assert observed_quota_growth(rows) == 5
    assert current_quota_cycle_start([rows[0]], 10080) is None


@pytest.mark.parametrize(
    ("plan", "capacity", "window_minutes"),
    [("pro", 7560 * 20, 10080), ("plus", 7560, 10080), ("team", 7560, 10080), ("free", 1134, 43200)],
)
def test_estimate_scales_with_any_long_window_capacity(plan: str, capacity: float, window_minutes: int) -> None:
    rows = [_row(plan, 1, 50, window_minutes / 1440)]
    estimate = estimate_quota_lb_share(
        account_id=plan,
        target_rows=rows,
        target_capacity_credits=capacity,
        window_minutes=window_minutes,
        reference_rows={"peer": [_row("peer", 0, 0, 7), _row("peer", 1, 50, 7)]},
        reference_capacities={"peer": 7560},
        costs_by_account={plan: capacity * 0.25 * 0.01, "peer": 37.8},
    )
    assert estimate is not None
    assert estimate.estimated_lb_share_percent == pytest.approx(50)
    assert estimate.observed_used_credits == capacity / 2
    assert estimate.window_minutes == window_minutes


def test_reset_within_a_day_and_old_deadline_replay() -> None:
    rows = [_row("target", 0, 55, 7), _row("target", 1, 55, 7 + 1 / 24), _row("target", 2, 60, 7 + 1 / 24)]
    assert current_quota_cycle_start(rows, 10080) == BASE + timedelta(hours=1)
    assert observed_quota_growth(rows) == 60
    old = _row("target", 3, 90, 7)
    assert current_quota_cycle_start([*rows, old], 10080) is None
    assert observed_quota_growth([*rows, old]) == 60


def test_minute_deadline_drift_does_not_renew_a_busy_cycle() -> None:
    rows = [_row("target", 1, 10, 7), _row("target", 48, 15, 7 + 1 / 1440)]
    assert current_quota_cycle_start(rows, 10080) == BASE
    assert observed_quota_growth(rows) == 5


def test_missing_deadline_does_not_make_expired_usage_fresh() -> None:
    rows = [_row("target", 0, 55, 7), _row("target", 169, 55, None)]
    assert current_quota_cycle_start(rows, 10080) is None
    assert _estimate(rows) is None


def test_one_point_correction_to_zero_waits_for_deadline_confirmation() -> None:
    rows = [_row("target", 1, 1, 7), _row("target", 2, 0, 7), _row("target", 3, 1, 7)]
    assert current_quota_cycle_start(rows, 10080) == BASE
    assert observed_quota_growth(rows) == 0


def test_a_quiet_zero_cycle_cannot_retain_an_old_boundary_after_renewal() -> None:
    rows = [_row("target", 0, 0, 7), _row("target", 25, 0, 7), _row("target", 26, 5, 8)]
    assert current_quota_cycle_start(rows, 10080) == BASE + timedelta(hours=24)
