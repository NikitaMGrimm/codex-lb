"""Persist explicitly trusted LB-only quota calibration references."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20261005_180000_trusted_lb_calibration_references"
down_revision = "20260930_010000_merge_vps_attribution_and_upstream_heads"
branch_labels = None
depends_on = None

_COLUMN = "quota_lb_share_reference_account_ids_json"


def upgrade() -> None:
    # Recovery can encounter current model-created tables with a lost ledger.
    existing = next(
        (c for c in sa.inspect(op.get_bind()).get_columns("dashboard_settings") if c["name"] == _COLUMN), None
    )
    if existing is not None:
        if not isinstance(existing["type"], sa.Text) or existing["nullable"]:
            raise RuntimeError("Incompatible trusted LB calibration reference column")
        return
    op.add_column("dashboard_settings", sa.Column(_COLUMN, sa.Text(), nullable=False, server_default=sa.text("'[]'")))


def downgrade() -> None:
    with op.batch_alter_table("dashboard_settings") as batch_op:
        batch_op.drop_column(_COLUMN)
