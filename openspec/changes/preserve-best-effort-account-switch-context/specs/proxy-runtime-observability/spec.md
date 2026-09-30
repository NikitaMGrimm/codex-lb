## ADDED Requirements

### Requirement: Best-effort replay stages are independently diagnosable

For owner-loss recovery, the proxy MUST emit low-cardinality structured
diagnostics for each rejected replay stage, the selected replay stage, and the
durable task-rebind outcome. Rejection and selection MUST be distinct events or
fields so operators can distinguish sanitized-history rejection from an
intentional newest-message fallback. Diagnostics MUST NOT include prompt text,
tool output, raw task keys, response IDs, account emails, or credentials.

#### Scenario: Sanitized history rejection and latest-message selection are visible

- **GIVEN** full-history projection fails account-neutral validation
- **AND** newest-message recovery succeeds
- **WHEN** the bridge switches accounts
- **THEN** logs identify the sanitized-history rejection reason separately
- **AND** logs identify the selected newest-message stage and durable-rebind
  outcome
