"""Add optional Pro weekly ratio for LB attribution only."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260930_000000_pro_weekly_attribution_ratio"
down_revision = "20260913_000000_merge_vps_and_usage_reserves"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("dashboard_settings") as batch_op:
        batch_op.add_column(sa.Column("pro_weekly_capacity_multiplier", sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("dashboard_settings") as batch_op:
        batch_op.drop_column("pro_weekly_capacity_multiplier")
