"""Join deployed VPS history with the refreshed usage-limit PR.

Revision ID: 20261022_190000_merge_vps_refresh_heads
Revises: 20261005_180000_trusted_lb_calibration_references, 20261002_010000_merge_usage_limit_review_heads
Create Date: 2026-10-22
"""

revision = "20261022_190000_merge_vps_refresh_heads"
down_revision = (
    "20261005_180000_trusted_lb_calibration_references",
    "20261002_010000_merge_usage_limit_review_heads",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
