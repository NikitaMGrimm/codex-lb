from __future__ import annotations

from datetime import timedelta, timezone

import pytest
from sqlalchemy import delete, update

from app.core.crypto import TokenEncryptor
from app.core.utils.time import utcnow
from app.db.models import Account, RequestLog, UsageHistory
from app.db.session import SessionLocal
from app.modules.dashboard.repository import DashboardRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_quota_lb_share_api_uses_successful_account_costs(async_client, db_setup) -> None:
    now = utcnow().replace(microsecond=0)
    start = now - timedelta(days=2)
    encryptor = TokenEncryptor()

    def account(account_id: str, plan: str) -> Account:
        return Account(
            id=account_id,
            email=f"{account_id}@example.com",
            plan_type=plan,
            access_token_encrypted=encryptor.encrypt("access"),
            refresh_token_encrypted=encryptor.encrypt("refresh"),
            id_token_encrypted=encryptor.encrypt("id"),
            last_refresh=now,
        )

    def observation(account_id: str, at, used: float, reset_day: int) -> UsageHistory:
        return UsageHistory(
            account_id=account_id,
            recorded_at=at,
            window="primary" if account_id == "pro" else "secondary",
            window_minutes=10080,
            used_percent=used,
            reset_at=int((start + timedelta(days=reset_day)).replace(tzinfo=timezone.utc).timestamp()),
        )

    async with SessionLocal() as session:
        session.add_all([account("pro", "pro"), account("plus", "plus"), account("team", "team")])
        session.add_all(
            [
                observation("pro", start, 100, 0),
                observation("pro", start + timedelta(seconds=30), 100, 0),
                observation("pro", start + timedelta(minutes=1), 0, 7),
                observation("pro", now - timedelta(minutes=1), 50, 7),
                observation("plus", start, 0, 7),
                observation("plus", start + timedelta(seconds=30), 0, 7),
                observation("plus", now - timedelta(minutes=1), 50, 7),
                observation("team", start, 0, 7),
                observation("team", start + timedelta(seconds=30), 0, 7),
                observation("team", now - timedelta(minutes=1), 50, 7),
            ]
        )
        for account_id, cost in (("pro", 400), ("plus", 40), ("team", 40)):
            session.add(
                RequestLog(
                    account_id=account_id,
                    request_id=f"successful-{account_id}",
                    model="gpt-6-sol",
                    status="success",
                    cost_usd=cost,
                    requested_at=start + timedelta(hours=1),
                )
            )
        session.add(
            RequestLog(
                account_id="pro",
                request_id="failed-pro",
                model="gpt-6-sol",
                status="error",
                cost_usd=999,
                requested_at=start + timedelta(hours=1),
            )
        )
        await session.commit()

    async with SessionLocal() as session:
        repository = DashboardRepository(session)
        baseline = await repository.latest_full_long_observation("pro", 10080, start, now)
        assert baseline is not None
        assert baseline.recorded_at == start + timedelta(seconds=30)
        assert await repository.latest_full_long_observation("pro", 10080, start + timedelta(minutes=1), now) is None
        rows = await repository.long_quota_observations({"pro": 10080, "plus": 10080, "team": 10080}, start, now)
        assert len(rows) == 10, rows
        costs = await repository.successful_costs_by_account(["pro", "plus", "team"], start, now)
        assert costs == {"pro": 400, "plus": 40, "team": 40}

    inconsistent = await async_client.get("/api/dashboard/quota-lb-share")
    assert inconsistent.status_code == 200
    assert inconsistent.json()["estimates"] == []
    setting = await async_client.put("/api/settings", json={"proWeeklyCapacityMultiplier": 20})
    assert setting.status_code == 200, setting.text

    response = await async_client.get("/api/dashboard/quota-lb-share")
    assert response.status_code == 200, response.text
    estimates = response.json()["estimates"]
    assert len(estimates) == 1
    assert estimates[0]["accountId"] == "pro"
    assert estimates[0]["observedUsedPercent"] == 50
    assert estimates[0]["observedUsedCredits"] == 75_600
    assert estimates[0]["windowMinutes"] == 10080
    assert estimates[0]["estimatedLbUsedPercent"] == pytest.approx(25)
    assert estimates[0]["estimatedLbSharePercent"] == pytest.approx(50)
    assert estimates[0]["referenceAccountCount"] == 2
    assert estimates[0]["since"].endswith("Z")
    assert estimates[0]["since"] == (start + timedelta(seconds=30)).isoformat() + "Z"

    async with SessionLocal() as session:
        await session.execute(
            update(UsageHistory)
            .where(UsageHistory.account_id == "pro", UsageHistory.used_percent == 50)
            .values(recorded_at=now - timedelta(minutes=10))
        )
        await session.commit()
    response = await async_client.get("/api/dashboard/quota-lb-share")
    assert response.status_code == 200
    assert response.json()["estimates"] == []

    async with SessionLocal() as session:
        await session.execute(
            delete(UsageHistory).where(UsageHistory.account_id == "pro", UsageHistory.used_percent == 100)
        )
        await session.execute(
            update(UsageHistory)
            .where(UsageHistory.account_id == "pro", UsageHistory.used_percent == 50)
            .values(recorded_at=now - timedelta(minutes=1))
        )
        await session.commit()
    response = await async_client.get("/api/dashboard/quota-lb-share")
    assert response.status_code == 200
    assert response.json()["estimates"] == []


@pytest.mark.asyncio
async def test_free_monthly_lb_share_uses_monthly_credit_capacity(async_client, db_setup) -> None:
    now = utcnow().replace(microsecond=0)
    start = now - timedelta(days=2)
    encryptor = TokenEncryptor()
    async with SessionLocal() as session:
        for account_id, plan in (("free", "free"), ("plus", "plus"), ("team", "team")):
            session.add(
                Account(
                    id=account_id,
                    email=f"{account_id}@example.com",
                    plan_type=plan,
                    access_token_encrypted=encryptor.encrypt("access"),
                    refresh_token_encrypted=encryptor.encrypt("refresh"),
                    id_token_encrypted=encryptor.encrypt("id"),
                    last_refresh=now,
                )
            )
            window = "monthly" if account_id == "free" else "secondary"
            window_minutes = 43200 if account_id == "free" else 10080
            reset = int(
                (start + timedelta(days=30 if account_id == "free" else 7)).replace(tzinfo=timezone.utc).timestamp()
            )
            observations = (
                (
                    (start, 100, int(start.replace(tzinfo=timezone.utc).timestamp())),
                    (start + timedelta(minutes=1), 0, reset),
                    (now - timedelta(minutes=1), 50, reset),
                )
                if account_id == "free"
                else ((start, 0, reset), (now - timedelta(minutes=1), 50, reset))
            )
            for recorded_at, used, reset_at in observations:
                session.add(
                    UsageHistory(
                        account_id=account_id,
                        window=window,
                        window_minutes=window_minutes,
                        recorded_at=recorded_at,
                        used_percent=used,
                        reset_at=reset_at,
                    )
                )
            session.add(
                RequestLog(
                    account_id=account_id,
                    request_id=f"successful-{account_id}",
                    model="gpt-6-sol",
                    status="success",
                    cost_usd=2.835 if account_id == "free" else 37.8,
                    requested_at=start + timedelta(hours=1),
                )
            )
        await session.commit()

    response = await async_client.get("/api/dashboard/quota-lb-share")
    assert response.status_code == 200, response.text
    estimates = response.json()["estimates"]
    assert len(estimates) == 1
    assert estimates[0]["accountId"] == "free"
    assert estimates[0]["windowMinutes"] == 43200
    assert estimates[0]["observedUsedCredits"] == pytest.approx(567)
    assert estimates[0]["estimatedLbSharePercent"] == pytest.approx(50)
