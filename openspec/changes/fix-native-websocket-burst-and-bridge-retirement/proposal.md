# Fix Native WebSocket Burst Failures and HTTP Bridge Retirement

## Why

Four defects compounded on one deployment while parallel Codex turns were streaming:

- HTTP bridge streams failed mid-response every 13-30 seconds with `Upstream websocket receive failed`, no close code and `stream_incomplete`. The native helper's per-connection WebSocket *message* queue was still capped at 64 frames; `bound-native-egress-stream-queue-by-bytes` moved only the event queue to a byte budget because the message queue had "never tripped in production". The pump forwards one frame per event-loop turn while a relay reader that spawns a task per `receive()` needs several turns per frame, so a burst of roughly a hundred buffered frames overflows the cap even with an idle consumer. The overflow is a local fault, but it was charged to the upstream account as a transient error.
- The failure could not be identified from logs: the adapter replaced the helper's failure phase and message with the fixed `Upstream websocket <operation> failed` and logged neither.
- Every reader failure was followed exactly one second later by `Timed out waiting for http bridge upstream reader cancellation`. The reader awaits its own retirement in a child task with cancellation deferred; the close inside that retirement cancels and awaits the session's reader, which is the task awaiting it, so the close waited out the whole cancel timeout while holding the session's lifecycle lock.
- A continuation pinned to a usage-limited durable owner was answered with HTTP 429 `account_usage_limit_reached` on every client retry although other accounts were eligible. Selection reports that denial as 429 (`account-routing`), but the bridge's account-neutral recovery predicate still required the 503 it carried before, so "Verified full resend may replace a usage-limited durable owner" never ran.

## What Changes

- The native WebSocket message queue uses the same bound as the event queue that feeds it: a 32 MiB queued-payload budget with a 4096-frame cap. Enqueueing stays non-blocking so send acknowledgements, which share the pump, cannot deadlock behind a full queue.
- The native WebSocket adapter logs the helper failure phase and message at WARNING. The relay-facing error message and code are unchanged.
- The HTTP bridge reader leaves the session's reader slot while it awaits a retirement it owns, and takes it back when the session survived.
- The bridge's owner-failure recovery predicate accepts `account_usage_limit_reached` with the 429 selection reports (and the earlier 503). Replay-safety rejection conditions are unchanged.

## Capabilities

### Modified Capabilities

- `outbound-http-clients`: native helper WebSocket message queue bound; failure-detail logging.
- `responses-api-compat`: HTTP bridge reader-owned retirement.
- `upstream-proxy-routing`: usage-limited owner recovery recognizes the selector's status.

## Impact

- `app/core/clients/native_egress.py`, `app/core/clients/proxy_websocket.py`, `app/modules/proxy/_service/http_bridge/upstream_events.py`, `app/modules/proxy/_service/http_bridge/streaming.py`; tests in `tests/unit/test_native_egress.py`, `tests/unit/test_proxy_websocket_client.py`, `tests/unit/test_proxy_http_bridge.py`.
- Worst-case queued memory per native WebSocket rises from 64 frames to 32 MiB on top of the event queue's 32 MiB; bytes are released as the consumer drains. No settings, schema, API or helper-protocol changes; the Rust helper is not rebuilt.
