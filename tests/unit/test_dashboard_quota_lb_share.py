from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.modules.dashboard.quota_lb_share import estimate_quota_lb_share, observed_quota_growth
from app.modules.dashboard.repository import QuotaObservation

BASE = datetime(2026, 9, 22, 9, 0)


def _row(account_id: str, hour: int, used: float, reset_day: int) -> QuotaObservation:
    return QuotaObservation(
        account_id=account_id,
        recorded_at=BASE + timedelta(hours=hour),
        used_percent=used,
        reset_at=int((BASE + timedelta(days=reset_day)).timestamp()),
    )


def test_estimate_counts_multiple_resets_and_uses_twenty_to_one_ratio() -> None:
    target = [
        _row("pro", 0, 100, 0),
        _row("pro", 1, 0, 7),
        _row("pro", 100, 55, 7),
        _row("pro", 101, 0, 11),
        _row("pro", 190, 99, 11),
        _row("pro", 191, 0, 15),
        _row("pro", 199, 6, 15),
    ]
    references = {
        "plus": [_row("plus", 0, 0, 7), _row("plus", 50, 50, 7), _row("plus", 150, 100, 7)],
        "team": [_row("team", 0, 0, 7), _row("team", 150, 100, 7)],
    }

    estimate = estimate_quota_lb_share(
        account_id="pro",
        target_rows=target,
        target_capacity_credits=7560 * 20,
        window_minutes=10080,
        reference_rows=references,
        reference_capacities={"plus": 7560, "team": 7560},
        costs_by_account={"pro": 1500, "plus": 80, "team": 80},
    )

    assert estimate is not None
    assert estimate.observed_used_percent == 160
    assert estimate.observed_used_credits == 160 * 7560 * 20 / 100
    assert estimate.window_minutes == 10080
    assert estimate.estimated_lb_used_percent == pytest.approx(93.75)
    assert estimate.estimated_lb_share_percent == pytest.approx(58.59375)
    assert estimate.reference_account_count == 2
    assert estimate.since == BASE


def test_small_quota_correction_does_not_create_false_growth() -> None:
    rows = [
        _row("peer", 0, 30, 7),
        _row("peer", 1, 29, 7),
        _row("peer", 2, 30, 7),
        _row("peer", 3, 35, 7),
        _row("peer", 4, 0, 11),
        _row("peer", 5, 4, 11),
    ]
    assert observed_quota_growth(rows) == 9


def test_reset_from_low_usage_starts_a_new_cycle() -> None:
    rows = [
        _row("pro", 0, 0, 7),
        _row("pro", 1, 6, 7),
        _row("pro", 2, 0, 11),
        _row("pro", 3, 3, 11),
    ]
    assert observed_quota_growth(rows) == 9


def test_missing_full_observation_or_references_omits_estimate() -> None:
    target = [_row("pro", 0, 100, 0), _row("pro", 1, 0, 7), _row("pro", 2, 50, 7)]
    peer = [_row("plus", 0, 0, 7), _row("plus", 2, 50, 7)]
    assert (
        estimate_quota_lb_share(
            account_id="pro",
            target_rows=target[1:],
            target_capacity_credits=7560 * 20,
            window_minutes=10080,
            reference_rows={"plus": peer},
            reference_capacities={"plus": 7560},
            costs_by_account={"pro": 100},
        )
        is None
    )
    assert (
        estimate_quota_lb_share(
            account_id="pro",
            target_rows=target,
            target_capacity_credits=7560 * 20,
            window_minutes=10080,
            reference_rows={"plus": peer},
            reference_capacities={"plus": 7560},
            costs_by_account={"pro": 100, "plus": 40},
        )
        is None
    )


def test_inconsistent_calibration_omits_estimate() -> None:
    target = [_row("pro", 0, 100, 0), _row("pro", 1, 0, 7), _row("pro", 2, 50, 7)]
    peer = [_row("plus", 0, 0, 7), _row("plus", 2, 50, 7)]
    team = [_row("team", 0, 0, 7), _row("team", 2, 50, 7)]
    assert (
        estimate_quota_lb_share(
            account_id="pro",
            target_rows=target,
            target_capacity_credits=7560 * 20,
            window_minutes=10080,
            reference_rows={"plus": peer, "team": team},
            reference_capacities={"plus": 7560, "team": 7560},
            costs_by_account={"pro": 10_000, "plus": 40, "team": 40},
        )
        is None
    )


@pytest.mark.parametrize(
    ("plan", "capacity", "window_minutes"),
    [
        ("pro", 7560 * 20, 10080),
        ("plus", 7560, 10080),
        ("team", 7560, 10080),
        ("free", 1134, 43200),
    ],
)
def test_estimate_scales_with_any_long_window_capacity(plan: str, capacity: float, window_minutes: int) -> None:
    target = [_row(plan, 0, 100, 0), _row(plan, 1, 0, 7), _row(plan, 2, 50, 7)]
    peers = {
        "peer-a": [_row("peer-a", 0, 0, 7), _row("peer-a", 2, 50, 7)],
        "peer-b": [_row("peer-b", 0, 0, 7), _row("peer-b", 2, 50, 7)],
    }
    estimate = estimate_quota_lb_share(
        account_id=plan,
        target_rows=target,
        target_capacity_credits=capacity,
        window_minutes=window_minutes,
        reference_rows=peers,
        reference_capacities={"peer-a": 7560, "peer-b": 7560},
        costs_by_account={plan: capacity * 0.25 * 0.01, "peer-a": 37.8, "peer-b": 37.8},
    )
    assert estimate is not None
    assert estimate.estimated_lb_share_percent == pytest.approx(50)
    assert estimate.observed_used_credits == capacity / 2
    assert estimate.window_minutes == window_minutes
