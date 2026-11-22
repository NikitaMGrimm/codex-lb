# upstream-proxy-routing Delta

## ADDED Requirements

### Requirement: Usage-limited owner recovery recognizes the selector's denial status

The HTTP bridge MUST treat an `account_usage_limit_reached` owner denial as eligible for the existing account-neutral recovery path when it carries HTTP 429, the status account selection reports for that code, and when it carries HTTP 503. Recognition MUST depend on the error code and those statuses only; every existing replay-safety rejection condition MUST still be evaluated before any account switch.

#### Scenario: Selector-reported 429 moves a verified full resend

- **GIVEN** an HTTP-bridge continuation is durably owned by one account
- **AND** the client supplies verified account-neutral full history
- **WHEN** the owner is rejected with HTTP 429 `account_usage_limit_reached` as built by the selection-failure mapper
- **THEN** the service excludes the usage-limited owner and continues on another eligible account

#### Scenario: Unsafe history stays on the owner under the same 429

- **GIVEN** the supplied history is not safe for fresh cross-account replay
- **WHEN** the owner is rejected with HTTP 429 `account_usage_limit_reached`
- **THEN** the service returns that rejection without moving the continuation
