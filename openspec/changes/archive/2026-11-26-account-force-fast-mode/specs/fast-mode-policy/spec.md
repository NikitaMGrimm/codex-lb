## ADDED Requirements

### Requirement: Operator-controlled Fast mode per subscription account

The Accounts dashboard SHALL expose a writable Force Fast mode switch for each subscription account to operators with account write permission. The switch SHALL persist on the account and SHALL default to off, including for accounts that predate the feature.

For each eligible Responses or compact dispatch on a selected account with Force Fast mode enabled, the proxy SHALL replace the request's service tier with priority, including when the client or API key specified another tier. The override SHALL respect the global Prohibit Fast Mode setting and SHALL leave the tier unchanged where an authoritative catalog shows that the selected account does not support priority for the model. Account selection and ownership constraints SHALL remain in effect.

#### Scenario: Standard request goes to an opted-in account

- **GIVEN** an account has Force Fast mode enabled and supports priority for the selected model
- **WHEN** a client requests Standard and that account is selected
- **THEN** the upstream attempt uses priority

#### Scenario: A retry lands on a different account

- **GIVEN** an attempt used priority because the selected account has Force Fast mode enabled
- **WHEN** a permitted retry selects an account with Force Fast mode off
- **THEN** the retry uses the tier it would have used without Force Fast mode

#### Scenario: Operator changes the setting on an existing connection

- **GIVEN** an account has a reusable upstream WebSocket
- **WHEN** an operator changes Force Fast mode
- **THEN** new requests on that connection use the updated account setting
