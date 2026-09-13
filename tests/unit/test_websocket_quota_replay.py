import json

import pytest

from app.modules.proxy import service as proxy_service
from app.modules.proxy._service.websocket.helpers import _prepare_websocket_quota_account_switch


@pytest.mark.parametrize("blocker", ["file", "previous_response", "visible", "accepted", "missing_tool_call"])
def test_quota_replay_preserves_ownership_and_output_guards(blocker):
    payload = {"type": "response.create", "model": "gpt-6-astra", "input": [{"role": "user", "content": "hello"}]}
    state = proxy_service._WebSocketRequestState(
        request_id="quota-guard",
        model="gpt-6-astra",
        service_tier=None,
        reasoning_effort="low",
        api_key_reservation=None,
        started_at=0.0,
        request_text=json.dumps(payload),
        awaiting_response_created=True,
        preferred_account_id="owner",
        replay_required_account_id="owner",
    )
    if blocker == "file":
        state.file_required_preferred_account = True
    elif blocker == "previous_response":
        state.previous_response_id = "resp-owned"
    elif blocker == "visible":
        state.downstream_visible = True
    elif blocker == "accepted":
        state.response_id = "resp-accepted"
    else:
        payload["input"] = [{"type": "function_call_output", "call_id": "missing", "output": "result"}]
        state.request_text = json.dumps(payload)
    original = state.request_text
    assert _prepare_websocket_quota_account_switch(state) is None
    assert state.replay_required_account_id == "owner"
    assert state.request_text == original
