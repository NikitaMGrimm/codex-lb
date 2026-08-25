"""merge deployed account usage limits and beta.4 heads

Revision ID: 20260825_000000_merge_account_usage_limits_and_beta4_heads
Revises:
- 20260728_010000_add_account_usage_limits
- 20260816_000000_add_model_source_embeddings
Create Date: 2026-08-25

The account usage-limit revision was deployed before the beta.4 migration
lineage was incorporated. Keep that applied revision's ancestry immutable and
join it to the new upstream head with this no-op merge.
"""

from __future__ import annotations

revision = "20260825_000000_merge_account_usage_limits_and_beta4_heads"
down_revision = (
    "20260728_010000_add_account_usage_limits",
    "20260816_000000_add_model_source_embeddings",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
