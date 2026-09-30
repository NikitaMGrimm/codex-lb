"""merge deployed usage limits and retry-circuit heads

Revision ID: 20260827_000000_merge_deployed_usage_limits_and_retry_circuit_heads
Revises:
- 20260825_000000_merge_account_usage_limits_and_beta4_heads
- 20260821_000000_add_retry_circuit_admission_generation
Create Date: 2026-08-27

The production database already applied the account usage-limit branch and
its beta.4 merge revision. Keep both applied revisions immutable and join the
newer upstream retry-circuit head with this no-op successor.
"""

from __future__ import annotations

revision = "20260827_000000_merge_deployed_usage_limits_and_retry_circuit_heads"
down_revision = (
    "20260825_000000_merge_account_usage_limits_and_beta4_heads",
    "20260821_000000_add_retry_circuit_admission_generation",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
