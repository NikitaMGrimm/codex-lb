from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete, update

from app.core.crypto import TokenEncryptor
from app.core.utils.time import utcnow
from app.db.models import Account, DashboardSettings, RequestLog, UsageHistory
from app.db.session import SessionLocal
from app.modules.dashboard.repository import DashboardRepository

pytestmark = pytest.mark.integration


async def _seed(*, target_plan: str = "pro", current_used: float = 5) -> tuple[datetime, datetime, int]:
    now = utcnow().replace(microsecond=0)
    start = now - timedelta(days=1)
    encryptor = TokenEncryptor()
    duration = 30 if target_plan == "free" else 7
    deadline = int((start + timedelta(days=duration)).replace(tzinfo=timezone.utc).timestamp())
    async with SessionLocal() as session:
        session.add_all(
            [
                Account(
                    id=aid,
                    email=f"{aid}@example.com",
                    plan_type=plan,
                    access_token_encrypted=encryptor.encrypt("access"),
                    refresh_token_encrypted=encryptor.encrypt("refresh"),
                    id_token_encrypted=encryptor.encrypt("id"),
                    last_refresh=now,
                )
                for aid, plan in (("target", target_plan), ("peer", "plus"))
            ]
        )
        for aid, used, at, reset in (
            ("target", 55, start - timedelta(minutes=1), deadline - 3 * 86400),
            # Equal percentages around an early reset must survive edge compression.
            ("target", 55, start, deadline),
            ("target", 55, start + timedelta(minutes=1), deadline),
            ("target", current_used, now - timedelta(minutes=1), deadline),
            (
                "peer",
                0,
                start - timedelta(hours=1),
                int((start + timedelta(days=7)).replace(tzinfo=timezone.utc).timestamp()),
            ),
            (
                "peer",
                10,
                now - timedelta(minutes=1),
                int((start + timedelta(days=7)).replace(tzinfo=timezone.utc).timestamp()),
            ),
        ):
            session.add(
                UsageHistory(
                    account_id=aid,
                    recorded_at=at,
                    window="monthly"
                    if aid == "target" and target_plan == "free"
                    else "primary"
                    if aid == "target"
                    else "secondary",
                    window_minutes=duration * 1440 if aid == "target" else 10080,
                    used_percent=used,
                    reset_at=reset,
                )
            )
        for aid, cost, at, status in (
            ("target", 999, start - timedelta(seconds=10), "success"),
            ("target", 7.56 if target_plan != "free" else 0.567, start + timedelta(hours=1), "success"),
            ("target", 999, start + timedelta(hours=1), "error"),
            ("target", 999, now, "success"),  # beyond the quota observation
            ("peer", 7.56, start + timedelta(hours=1), "success"),
        ):
            session.add(
                RequestLog(
                    account_id=aid,
                    request_id=f"{aid}-{status}-{at}",
                    model="gpt-6-sol",
                    status=status,
                    cost_usd=cost,
                    requested_at=at,
                )
            )
        await session.execute(
            update(DashboardSettings).values(
                pro_weekly_capacity_multiplier=20, quota_lb_share_reference_account_ids_json='["peer"]'
            )
        )
        await session.commit()
    return now, start, deadline


@pytest.mark.asyncio
async def test_current_cycle_api_excludes_old_failed_and_not_yet_observed_costs(async_client, db_setup) -> None:
    now, start, deadline = await _seed()
    async with SessionLocal() as session:
        rows = await DashboardRepository(session).long_quota_observations(
            {"target": 10080}, start - timedelta(hours=1), now
        )
        assert len(rows) == 4  # reset edge survives identical usage rows
    response = await async_client.get("/api/dashboard/quota-lb-share")
    assert response.status_code == 200
    estimate = next(e for e in response.json()["estimates"] if e["accountId"] == "target")
    assert estimate["since"] == start.isoformat() + "Z"
    assert estimate["observedUsedPercent"] == 5
    assert estimate["observedUsedCredits"] == 7560
    assert estimate["estimatedLbUsedCredits"] == pytest.approx(756)
    assert estimate["estimatedLbSharePercent"] == pytest.approx(10)
    assert estimate["referenceAccountCount"] == 1
    assert estimate["resetAt"] == (start + timedelta(days=7)).isoformat() + "Z"

    # A new renewal replaces both the numerator and denominator, even when
    # the first observed usage is higher than the previous cycle's last use.
    renewed = now - timedelta(seconds=30)
    renewed_reset = int((renewed + timedelta(days=7)).replace(tzinfo=timezone.utc).timestamp())
    async with SessionLocal() as session:
        session.add(
            UsageHistory(
                account_id="target",
                window="primary",
                window_minutes=10080,
                recorded_at=renewed,
                used_percent=10,
                reset_at=renewed_reset,
            )
        )
        session.add(
            RequestLog(
                account_id="target",
                request_id="at-reset-boundary",
                model="gpt-6-sol",
                status="success",
                cost_usd=7.56,
                requested_at=renewed,
            )
        )
        await session.commit()
    response = await async_client.get("/api/dashboard/quota-lb-share")
    estimate = next(e for e in response.json()["estimates"] if e["accountId"] == "target")
    assert estimate["since"] == renewed.isoformat() + "Z"
    assert estimate["observedUsedPercent"] == 10
    assert estimate["estimatedLbSharePercent"] == pytest.approx(5)


@pytest.mark.asyncio
async def test_no_prior_full_observation_and_uncapped_share(async_client, db_setup) -> None:

    await _seed(target_plan="free")
    async with SessionLocal() as session:
        await session.execute(
            delete(UsageHistory).where(UsageHistory.account_id == "target", UsageHistory.used_percent == 55)
        )
        await session.execute(
            update(RequestLog)
            .where(RequestLog.account_id == "target", RequestLog.cost_usd == 0.567)
            .values(cost_usd=1.134)
        )
        await session.commit()
    response = await async_client.get("/api/dashboard/quota-lb-share")
    estimate = next(e for e in response.json()["estimates"] if e["accountId"] == "target")
    assert estimate["windowMinutes"] == 43200
    assert estimate["observedUsedPercent"] == 5
    assert estimate["estimatedLbSharePercent"] == pytest.approx(200)


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid", ["stale", "expired", "regressed"])
async def test_api_withholds_stale_or_old_cycle_data(async_client, db_setup, invalid: str) -> None:
    now, start, deadline = await _seed()
    async with SessionLocal() as session:
        if invalid == "stale":
            await session.execute(
                update(UsageHistory)
                .where(UsageHistory.account_id == "target", UsageHistory.used_percent == 5)
                .values(recorded_at=now - timedelta(minutes=10))
            )
        else:
            session.add(
                UsageHistory(
                    account_id="target",
                    window="primary",
                    window_minutes=10080,
                    recorded_at=now,
                    used_percent=55,
                    reset_at=int((now - timedelta(seconds=1)).replace(tzinfo=timezone.utc).timestamp())
                    if invalid == "expired"
                    else deadline - 3 * 86400,
                )
            )
        await session.commit()
    response = await async_client.get("/api/dashboard/quota-lb-share")
    assert not any(e["accountId"] == "target" for e in response.json()["estimates"])


@pytest.mark.asyncio
@pytest.mark.parametrize("used", [0, 5])
async def test_zero_lb_cost_is_available_without_peers(async_client, db_setup, used: float) -> None:

    await _seed(current_used=used)
    async with SessionLocal() as session:
        await session.execute(delete(RequestLog))
        await session.execute(delete(UsageHistory).where(UsageHistory.account_id == "peer"))
        await session.commit()
    response = await async_client.get("/api/dashboard/quota-lb-share")
    estimate = next(e for e in response.json()["estimates"] if e["accountId"] == "target")
    assert estimate["estimatedLbSharePercent"] == 0
    assert estimate["referenceAccountCount"] == 0


@pytest.mark.asyncio
async def test_api_expires_confirmed_deadline_during_metadata_gap(async_client, db_setup) -> None:
    now, _, _ = await _seed()
    deadline = int((now - timedelta(seconds=30)).replace(tzinfo=timezone.utc).timestamp())
    async with SessionLocal() as session:
        await session.execute(update(UsageHistory).where(UsageHistory.account_id == "target").values(reset_at=deadline))
        session.add(
            UsageHistory(
                account_id="target",
                window="primary",
                window_minutes=10080,
                recorded_at=now - timedelta(seconds=40),
                used_percent=5,
                reset_at=None,
            )
        )
        await session.commit()
    response = await async_client.get("/api/dashboard/quota-lb-share")
    assert response.status_code == 200
    assert not any(e["accountId"] == "target" for e in response.json()["estimates"])


@pytest.mark.asyncio
async def test_trusted_reference_settings_roundtrip_preserves_ratio_and_ignores_unknown_target(
    async_client, db_setup
) -> None:
    await _seed()
    response = await async_client.put(
        "/api/settings", json={"quotaLbShareReferenceAccountIds": ["peer", "peer", "target"]}
    )
    assert response.status_code == 200
    assert response.json()["quotaLbShareReferenceAccountIds"] == ["peer", "target"]
    assert response.json()["proWeeklyCapacityMultiplier"] == 20
    # Target is configured too, but must be excluded from its own conversion.
    response = await async_client.get("/api/dashboard/quota-lb-share")
    estimate = next(e for e in response.json()["estimates"] if e["accountId"] == "target")
    assert estimate["estimatedLbSharePercent"] == pytest.approx(10)
    assert estimate["referenceAccountCount"] == 1
    response = await async_client.put("/api/settings", json={"proWeeklyCapacityMultiplier": 10})
    assert response.status_code == 200
    assert response.json()["quotaLbShareReferenceAccountIds"] == ["peer", "target"]
    response = await async_client.get("/api/dashboard/quota-lb-share")
    estimate = next(e for e in response.json()["estimates"] if e["accountId"] == "target")
    assert estimate["estimatedLbSharePercent"] == pytest.approx(20)


@pytest.mark.asyncio
async def test_no_trusted_reference_disables_positive_cost_estimates(async_client, db_setup) -> None:
    await _seed()
    response = await async_client.put("/api/settings", json={"quotaLbShareReferenceAccountIds": []})
    assert response.status_code == 200
    assert (await async_client.get("/api/dashboard/quota-lb-share")).json()["estimates"] == []


@pytest.mark.asyncio
async def test_only_selected_peer_current_cycle_affects_calibration(async_client, db_setup) -> None:
    now, start, deadline = await _seed()
    async with SessionLocal() as session:
        # Old-cycle peer growth and requests must not influence conversion.
        session.add_all(
            [
                UsageHistory(
                    account_id="peer",
                    window="secondary",
                    window_minutes=10080,
                    recorded_at=start - timedelta(days=3),
                    used_percent=80,
                    reset_at=deadline - 3 * 86400,
                ),
                RequestLog(
                    account_id="peer",
                    request_id="old-clean-cost",
                    model="gpt-6-sol",
                    status="success",
                    requested_at=start - timedelta(days=2),
                    cost_usd=1000,
                ),
            ]
        )
        await session.commit()
    response = await async_client.get("/api/dashboard/quota-lb-share")
    estimate = next(e for e in response.json()["estimates"] if e["accountId"] == "target")
    assert estimate["estimatedLbSharePercent"] == pytest.approx(10)
