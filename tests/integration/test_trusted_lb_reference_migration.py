from __future__ import annotations

import pytest
import sqlalchemy as sa
from alembic import command
from anyio import to_thread
from sqlalchemy.ext.asyncio import create_async_engine

from app.db.migrate import _build_alembic_config, run_upgrade

pytestmark = pytest.mark.integration
_PARENT = "20260930_010000_merge_vps_attribution_and_upstream_heads"
_COLUMN = "quota_lb_share_reference_account_ids_json"


@pytest.mark.asyncio
async def test_reference_column_upgrade_downgrade_preserves_ratio(tmp_path) -> None:
    url = f"sqlite+aiosqlite:///{tmp_path / 'references.sqlite'}"
    await to_thread.run_sync(lambda: run_upgrade(url, _PARENT, bootstrap_legacy=True))
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            await conn.execute(sa.text("UPDATE dashboard_settings SET pro_weekly_capacity_multiplier=7 WHERE id=1"))
        await to_thread.run_sync(lambda: run_upgrade(url, "head", bootstrap_legacy=True))
        async with engine.connect() as conn:
            row = (
                await conn.execute(sa.text(f"SELECT {_COLUMN}, pro_weekly_capacity_multiplier FROM dashboard_settings"))
            ).one()
            assert tuple(row) == ("[]", 7)
        await to_thread.run_sync(lambda: command.downgrade(_build_alembic_config(url), _PARENT))
        async with engine.connect() as conn:
            columns = await conn.run_sync(
                lambda c: {v["name"] for v in sa.inspect(c).get_columns("dashboard_settings")}
            )
            assert _COLUMN not in columns
            assert (
                await conn.execute(sa.text("SELECT pro_weekly_capacity_multiplier FROM dashboard_settings"))
            ).scalar_one() == 7
        await to_thread.run_sync(lambda: run_upgrade(url, "head", bootstrap_legacy=True))
    finally:
        await engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("nullable", [False, True])
async def test_recovery_reference_column_requires_compatible_shape(tmp_path, nullable: bool) -> None:
    url = f"sqlite+aiosqlite:///{tmp_path / 'existing-references.sqlite'}"
    await to_thread.run_sync(lambda: run_upgrade(url, _PARENT, bootstrap_legacy=True))
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            suffix = "" if nullable else " NOT NULL DEFAULT '[]'"
            await conn.execute(sa.text(f"ALTER TABLE dashboard_settings ADD COLUMN {_COLUMN} TEXT{suffix}"))
        if nullable:
            with pytest.raises(RuntimeError, match="Incompatible trusted"):
                await to_thread.run_sync(lambda: run_upgrade(url, "head", bootstrap_legacy=True))
        else:
            await to_thread.run_sync(lambda: run_upgrade(url, "head", bootstrap_legacy=True))
    finally:
        await engine.dispose()
