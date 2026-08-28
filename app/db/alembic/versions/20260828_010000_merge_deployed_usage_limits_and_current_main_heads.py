"""merge deployed usage limits and current main heads

Revision ID: 20260828_010000_merge_deployed_usage_limits_and_current_main_heads
Revises:
- 20260827_000000_merge_deployed_usage_limits_and_retry_circuit_heads
- 20260828_000000_add_accounts_chatgpt_identity_index
Create Date: 2026-08-28

Production already applied the custom account usage-limit lineage through the
20260827 merge revision. Keep that history immutable and join it to the current
upstream main head with this no-op successor.
"""

from __future__ import annotations

revision = "20260828_010000_merge_deployed_usage_limits_and_current_main_heads"
down_revision = (
    "20260827_000000_merge_deployed_usage_limits_and_retry_circuit_heads",
    "20260828_000000_add_accounts_chatgpt_identity_index",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
