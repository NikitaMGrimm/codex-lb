# outbound-http-clients Delta

## ADDED Requirements

### Requirement: Native helper WebSocket messages are bounded per connection by a byte budget

Frames the native egress helper relays for one WebSocket MUST be buffered between that connection's pump and its consumer in a queue bounded by the same queued-payload byte budget (32 MiB) and frame-count cap (4096) as the per-request event queue. Queued bytes MUST be released as the consumer drains. A burst of frames that fits the budget MUST NOT fail a consumer that is still draining, including a consumer that needs several event-loop turns per frame. Enqueueing MUST NOT block the pump, so send acknowledgements carried by the same pump are never delayed behind a full queue. Only when the queue exceeds its bound MAY the connection fail with `consumer_backpressure`.

#### Scenario: Burst of frames drains through a task-per-receive reader

- **GIVEN** the helper has 1000 text frames for one WebSocket buffered in its output pipe
- **WHEN** the consumer reads them by starting one task per `receive()`
- **THEN** the consumer receives every frame in order followed by the close
- **AND** the connection is not failed

#### Scenario: A consumer that stops draining is still bounded

- **GIVEN** a WebSocket whose consumer does not read while frames arrive
- **WHEN** the queued frames exceed the bound
- **THEN** the connection fails with `consumer_backpressure`

### Requirement: Native WebSocket transport failures keep their helper detail observable

When a native helper WebSocket send or receive fails, the adapter MUST log the helper failure phase and failure message at WARNING before returning its relay-facing error. The relay-facing error message and error code MUST remain unchanged.

#### Scenario: Receive failure is logged with its phase

- **WHEN** a native WebSocket receive fails with phase `consumer_backpressure`
- **THEN** the relay receives the generic receive-failed error with no adapter error code
- **AND** a WARNING log records `failure_phase=consumer_backpressure` and the helper message
