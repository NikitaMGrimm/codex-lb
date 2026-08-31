from __future__ import annotations

from app.core.usage.account_limits import AccountUsageLimitState, evaluate_standard_usage_limit
from app.db.models import AccountStatus
from app.modules.proxy.repo_bundle import ProxyRepoFactory

_UNAVAILABLE_STATUSES = frozenset({AccountStatus.PAUSED, AccountStatus.REAUTH_REQUIRED, AccountStatus.DEACTIVATED})


async def load_fresh_owner_usage_limit(
    repo_factory: ProxyRepoFactory,
    account_id: str,
    *,
    refresh_interval_seconds: int,
) -> AccountUsageLimitState | None:
    """Load one owner's policy and usage windows in one database statement."""
    async with repo_factory() as repos:
        snapshot = await repos.usage.account_usage_limit_snapshot(account_id)
    if snapshot is None or snapshot.status in _UNAVAILABLE_STATUSES:
        return None
    return evaluate_standard_usage_limit(
        enabled=snapshot.enabled,
        limit_percent=snapshot.limit_percent,
        plan_type=snapshot.plan_type,
        primary=snapshot.primary,
        secondary=snapshot.secondary,
        monthly=snapshot.monthly,
        refresh_interval_seconds=refresh_interval_seconds,
    )
