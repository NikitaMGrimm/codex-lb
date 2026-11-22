# Tasks

- [x] 1.1 Native WebSocket message queue uses `_BoundedEventQueue` (4096 frames / 32 MiB) with a message payload size; `put_nowait` is kept.
- [x] 1.2 `_native_websocket_transport_error` logs `failure_phase`, error type and helper message at WARNING; returned message and code unchanged.
- [x] 1.3 The bridge reader yields the session's reader slot around both retirement child tasks and restores it when the upstream close was not claimed.
- [x] 1.4 `_http_bridge_owner_error_allows_account_neutral_replay` accepts `account_usage_limit_reached` with 429 or 503.
- [x] 2.1 Tests: a 1000-frame burst drains through a task-per-receive reader; a consumer that stops draining still fails with `consumer_backpressure`; the adapter logs the helper detail behind the generic message; a failing registered reader retires without the cancellation-timeout warning; the usage-limited owner replay test builds its error through `selection_failure_response`.
- [x] 2.2 ruff, ty, strict OpenSpec validation.
