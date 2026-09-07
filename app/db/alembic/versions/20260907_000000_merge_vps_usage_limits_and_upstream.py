"""Join the immutable deployed usage-limit lineage to current upstream."""

from __future__ import annotations

revision = "20260907_000000_merge_vps_usage_limits_and_upstream"
down_revision = (
    "20260828_010000_merge_deployed_usage_limits_and_current_main_heads",
    "20260830_000000_add_quota_warmup_claim_expiry",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
