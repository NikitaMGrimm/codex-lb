"""Merge the deployed VPS attribution line with current upstream."""

revision = "20260930_010000_merge_vps_attribution_and_upstream_heads"
down_revision = (
    "20260918_000000_merge_scim_and_overflow_heads",
    "20260930_000000_pro_weekly_attribution_ratio",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
