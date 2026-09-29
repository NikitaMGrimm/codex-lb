from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from app.core.clients.proxy import ProxyResponseError
from app.modules.proxy._service.support import _check_account_usage_limit
from app.modules.proxy.load_balancer import LoadBalancer

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("cancel", [False, True], ids=["deadline", "caller-cancellation"])
async def test_usage_authorization_bounds_and_cancels_its_read(cancel: bool) -> None:
    started = asyncio.Event()
    stopped = asyncio.Event()

    async def stalled_read(_account_id: str) -> None:
        started.set()
        try:
            await asyncio.Future()
        finally:
            stopped.set()

    balancer = AsyncMock(spec=LoadBalancer)
    balancer.check_account_usage_limit.side_effect = stalled_read
    authorization = asyncio.create_task(
        _check_account_usage_limit(balancer, "account", deadline=time.monotonic() + (60.0 if cancel else 0.02))
    )
    await started.wait()
    if cancel:
        authorization.cancel()
        with pytest.raises(asyncio.CancelledError):
            await authorization
    else:
        with pytest.raises(ProxyResponseError) as error:
            await authorization
        assert error.value.status_code == 503
        assert error.value.payload["error"]["code"] == "account_usage_limit_authorization_failed"
    assert stopped.is_set()
