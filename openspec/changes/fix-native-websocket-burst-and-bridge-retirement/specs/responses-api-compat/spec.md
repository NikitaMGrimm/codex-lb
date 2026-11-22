# responses-api-compat Delta

## ADDED Requirements

### Requirement: HTTP bridge reader-owned retirement does not wait on its own reader

When an HTTP bridge upstream reader fails and awaits a retirement or poison settlement that it started, the session close performed by that retirement MUST NOT wait for the cancellation of the reader that is awaiting it. The reader MUST leave the session's reader slot for the duration of the awaited task and MUST take the slot back when the session's upstream close was not claimed, so a later reconnect still drains that reader before starting a replacement.

#### Scenario: Reader failure retires without a cancellation timeout

- **GIVEN** an HTTP bridge session whose registered upstream reader receives a transport error with no admission waiter
- **WHEN** the reader fails its pending requests and retires the session
- **THEN** the upstream WebSocket is closed and the session is detached
- **AND** no reader-cancellation timeout is logged
