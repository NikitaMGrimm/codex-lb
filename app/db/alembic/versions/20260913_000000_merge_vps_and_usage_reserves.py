"""Merge preserved VPS lineage, upstream, and per-window reserves."""

from __future__ import annotations

revision = "20260913_000000_merge_vps_and_usage_reserves"
down_revision = (
    "20260907_000000_merge_vps_usage_limits_and_upstream",
    "20260912_010000_drop_legacy_dashboard_credentials",
    "20260910_010000_add_usage_limit_overrides",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
