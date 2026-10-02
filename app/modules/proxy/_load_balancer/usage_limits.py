from __future__ import annotations

from typing import Mapping, Protocol

from app.core import usage as usage_core
from app.core.clock import Clock
from app.core.crypto import TokenEncryptor
from app.core.usage import refresh_policy
from app.core.usage.account_limits import AccountUsageLimitState
from app.db.models import Account, AccountStatus, AdditionalUsageHistory, UsageHistory
from app.modules.proxy._load_balancer.sticky_selection import SelectionInputsProtocol
from app.modules.proxy.account_cache import AccountSelectionCache
from app.modules.proxy.account_eligibility import account_access_token_expires_at
from app.modules.usage.mappers import evaluate_account_usage_limit


class UsageLimitOwner(Protocol):
    _clock: Clock
    _encryptor: TokenEncryptor

    @property
    def _selection_inputs_cache(self) -> AccountSelectionCache: ...

    async def _load_selection_inputs(
        self, *, model: str | None, clone_cached: bool = True
    ) -> SelectionInputsProtocol: ...


async def check_account_usage_limit(
    owner: UsageLimitOwner, account_id: str, *, max_attempts: int
) -> AccountUsageLimitState | None:
    """Authorize a continuity owner from a stable selection snapshot."""
    for _ in range(max_attempts):
        generation = owner._selection_inputs_cache.generation
        selection_inputs = await owner._load_selection_inputs(model=None, clone_cached=False)
        if generation != owner._selection_inputs_cache.generation:
            continue
        account = selection_inputs.runtime_account(account_id)
        if account is None or account.status in {
            AccountStatus.DEACTIVATED,
            AccountStatus.PAUSED,
        }:
            return None
        if account.status == AccountStatus.REAUTH_REQUIRED:
            expires_at = account_access_token_expires_at(account, owner._encryptor)
            if expires_at is not None and expires_at <= owner._clock.time():
                return None
        return evaluate_account_usage_limit(
            account,
            primary=standard_usage_entry(
                selection_inputs.latest_primary, selection_inputs.standard_latest_primary, account_id
            ),
            secondary=standard_usage_entry(
                selection_inputs.latest_secondary, selection_inputs.standard_latest_secondary, account_id
            ),
            monthly=selection_inputs.latest_monthly.get(account_id),
            refresh_interval_seconds=refresh_policy.USAGE_REFRESH_INTERVAL_SECONDS,
            now=owner._clock.now(),
        )
    raise RuntimeError("Account selection state changed during usage authorization")


def standard_usage_entry(
    request_priority: Mapping[str, UsageHistory | AdditionalUsageHistory],
    retained_standard: Mapping[str, UsageHistory] | None,
    account_id: str,
) -> UsageHistory | None:
    priority_entry = request_priority.get(account_id)
    if isinstance(priority_entry, UsageHistory):
        return priority_entry
    return retained_standard.get(account_id) if retained_standard is not None else None


def select_long_window_entry(
    *,
    account: Account,
    monthly_entry: UsageHistory | None,
    secondary_entry: UsageHistory | AdditionalUsageHistory | None,
) -> UsageHistory | AdditionalUsageHistory | None:
    if monthly_entry is not None and usage_core.capacity_for_plan(account.plan_type, "monthly") is not None:
        return monthly_entry
    return secondary_entry
