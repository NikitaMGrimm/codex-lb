from __future__ import annotations

import pytest
import sqlalchemy as sa
from alembic import command
from anyio import to_thread
from sqlalchemy.ext.asyncio import create_async_engine

from app.db.migrate import _build_alembic_config, run_upgrade

pytestmark = pytest.mark.integration

_PARENT = "20260913_000000_merge_vps_and_usage_reserves"
_COLUMN = "pro_weekly_capacity_multiplier"


@pytest.mark.asyncio
async def test_pro_attribution_ratio_column_upgrade_and_downgrade(tmp_path) -> None:
    url = f"sqlite+aiosqlite:///{tmp_path / 'pro-attribution-ratio.sqlite'}"
    await to_thread.run_sync(lambda: run_upgrade(url, _PARENT, bootstrap_legacy=True))
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            before = await conn.run_sync(
                lambda sync_conn: {c["name"] for c in sa.inspect(sync_conn).get_columns("dashboard_settings")}
            )
        assert _COLUMN not in before

        await to_thread.run_sync(lambda: run_upgrade(url, "head", bootstrap_legacy=True))
        async with engine.connect() as conn:
            upgraded = await conn.run_sync(
                lambda sync_conn: {c["name"] for c in sa.inspect(sync_conn).get_columns("dashboard_settings")}
            )
        assert _COLUMN in upgraded

        await to_thread.run_sync(lambda: command.downgrade(_build_alembic_config(url), _PARENT))
        async with engine.connect() as conn:
            downgraded = await conn.run_sync(
                lambda sync_conn: {c["name"] for c in sa.inspect(sync_conn).get_columns("dashboard_settings")}
            )
        assert _COLUMN not in downgraded
    finally:
        await engine.dispose()
