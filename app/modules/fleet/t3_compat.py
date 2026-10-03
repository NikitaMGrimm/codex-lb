"""Read-only CLIProxyAPI projection for T3's pooled quota display."""

from __future__ import annotations

import json
from typing import Literal

from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel

from app.core.auth.dependencies import set_dashboard_error_format, validate_usage_api_key
from app.core.exceptions import DashboardBadRequestError, DashboardPermissionError
from app.dependencies import AccountsContext, get_accounts_context
from app.modules.api_keys.service import ApiKeyData
from app.modules.fleet.api import _can_view_fleet_usage, get_fleet_summary
from app.modules.fleet.schemas import FleetWindowSummary

router = APIRouter(
    prefix="/v0/management",
    tags=["fleet"],
    dependencies=[Depends(set_dashboard_error_format)],
)

_USAGE_URL = "https://chatgpt.com/backend-api/wham/usage"
_CREDITS_URL = "https://chatgpt.com/backend-api/wham/rate-limit-reset-credits"


class T3AuthFile(BaseModel):
    id: str
    auth_index: str
    provider: Literal["codex"] = "codex"
    email: str
    disabled: bool = False
    id_token: dict[str, str]


class T3AuthFiles(BaseModel):
    files: list[T3AuthFile]


class T3ApiCall(BaseModel):
    auth_index: str
    method: Literal["GET"]
    url: str


class T3ApiResponse(BaseModel):
    status_code: int
    body: str


async def _require_quota_visibility(api_key: ApiKeyData) -> None:
    if not await _can_view_fleet_usage(api_key):
        raise DashboardPermissionError("Account quota visibility is disabled for this API key")


def _window(window: FleetWindowSummary) -> dict[str, float | int | None] | None:
    if window.remaining_percent is None:
        return None
    return {
        "used_percent": 100 - window.remaining_percent,
        "reset_at": int(window.reset_at.timestamp()) if window.reset_at is not None else None,
        "limit_window_seconds": window.window_minutes * 60 if window.window_minutes is not None else None,
    }


@router.get("/auth-files", response_model=T3AuthFiles)
async def t3_auth_files(
    context: AccountsContext = Depends(get_accounts_context),
    api_key: ApiKeyData = Security(validate_usage_api_key),
) -> T3AuthFiles:
    await _require_quota_visibility(api_key)
    summary = await get_fleet_summary(context, api_key)
    return T3AuthFiles(
        files=[
            T3AuthFile(
                id=account.account_id,
                auth_index=account.account_id,
                email=account.email,
                id_token={"chatgpt_plan_type": account.plan_type},
            )
            for account in summary.accounts
        ]
    )


@router.post("/api-call", response_model=T3ApiResponse)
async def t3_api_call(
    payload: T3ApiCall,
    context: AccountsContext = Depends(get_accounts_context),
    api_key: ApiKeyData = Security(validate_usage_api_key),
) -> T3ApiResponse:
    await _require_quota_visibility(api_key)
    if payload.url not in {_USAGE_URL, _CREDITS_URL}:
        raise DashboardBadRequestError("Only Codex quota reads are supported")
    summary = await get_fleet_summary(context, api_key)
    account = next((item for item in summary.accounts if item.account_id == payload.auth_index), None)
    if account is None:
        raise DashboardBadRequestError("Account is not visible to this API key")
    if payload.url == _CREDITS_URL:
        return T3ApiResponse(status_code=200, body='{"credits":[]}')
    return T3ApiResponse(
        status_code=200,
        body=json.dumps(
            {
                "plan_type": account.plan_type,
                "rate_limit": {
                    "primary_window": _window(account.primary),
                    "secondary_window": _window(account.secondary),
                },
            }
        ),
    )
