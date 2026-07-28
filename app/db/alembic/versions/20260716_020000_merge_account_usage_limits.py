"""merge account usage limits with the upstream migration chain

Revision ID: 20260716_020000_merge_account_usage_limits
Revises: 20260716_010000_add_dashboard_retention_settings, 20260714_000000_add_account_usage_limits
Create Date: 2026-07-16
"""

from __future__ import annotations

revision = "20260716_020000_merge_account_usage_limits"
down_revision = (
    "20260716_010000_add_dashboard_retention_settings",
    "20260714_000000_add_account_usage_limits",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
