"""Add the per-account Fast mode switch."""

import sqlalchemy as sa
from alembic import op

revision = "20261126_000000_add_account_force_fast_mode"
down_revision = "20261022_190000_merge_vps_refresh_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("accounts", sa.Column("force_fast_mode", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("accounts", "force_fast_mode")
