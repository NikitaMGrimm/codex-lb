from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_pro_attribution_ratio_setting_round_trips_and_validates(async_client, db_setup) -> None:
    initial = await async_client.get("/api/settings")
    assert initial.status_code == 200, initial.text
    assert initial.json()["proWeeklyCapacityMultiplier"] is None

    updated = await async_client.put("/api/settings", json={"proWeeklyCapacityMultiplier": 20})
    assert updated.status_code == 200, updated.text
    assert updated.json()["proWeeklyCapacityMultiplier"] == 20
    assert (await async_client.get("/api/settings")).json()["proWeeklyCapacityMultiplier"] == 20

    invalid = await async_client.put("/api/settings", json={"proWeeklyCapacityMultiplier": 0})
    assert invalid.status_code == 422
    assert (await async_client.get("/api/settings")).json()["proWeeklyCapacityMultiplier"] == 20

    cleared = await async_client.put("/api/settings", json={"proWeeklyCapacityMultiplier": None})
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["proWeeklyCapacityMultiplier"] is None
