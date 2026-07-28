"""merge the deployed account usage limits head with later upstream migrations

Revision ID: 20260728_000000_merge_account_usage_limits_v2
Revises: 20260725_000000_add_http_bridge_pending_tool_calls, 20260716_020000_merge_account_usage_limits
Create Date: 2026-07-28
"""

from __future__ import annotations

revision = "20260728_000000_merge_account_usage_limits_v2"
down_revision = (
    "20260725_000000_add_http_bridge_pending_tool_calls",
    "20260716_020000_merge_account_usage_limits",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
