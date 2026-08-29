# upstream-proxy-routing Delta

## ADDED Requirements

### Requirement: Dispatch-only ownership may fail over before visible output

When an otherwise unpinned client-supplied Responses payload becomes
account-bound only because it was dispatched to the selected account, and that
account returns an existing failover-eligible failure before any response output
becomes visible, the service MUST release that dispatch-created ownership,
exclude the failed account, and retry the original payload on another eligible
account within the existing attempt and request budgets. The service MUST NOT
apply this exception to previous-response, turn-state, uploaded-file, or
single-account ownership, or after downstream-visible output.

#### Scenario: Nonportable full history survives a pre-visible quota failure

- **GIVEN** an unpinned client request contains history that is not provably account-neutral
- **AND** the first selected account returns a failover-eligible quota failure before visible output
- **WHEN** another account is eligible
- **THEN** the service releases only the ownership created by the failed dispatch
- **AND** it retries the original client payload on the other account
- **AND** subsequent soft affinity may re-anchor to the successful account

#### Scenario: Pre-existing hard ownership remains fail-closed

- **GIVEN** a request depends on a previous response, turn state, uploaded file, or single-account policy
- **WHEN** its required account fails
- **THEN** the service does not use dispatch-owner release to move the request to another account

### Requirement: Verified full resend may replace a usage-limited durable owner

When an HTTP-bridge continuation is bound to a durable owner that reaches its
configured account usage limit before the current request is submitted, the
service MUST use the existing account-neutral recovery path if and only if the
client payload is a verified full resend that is safe for fresh cross-account
replay. The service MUST exclude the usage-limited owner from replacement
selection and MUST preserve all existing replay-safety rejection conditions.

#### Scenario: Safe full history continues on another account

- **GIVEN** an HTTP-bridge continuation is durably owned by one account
- **AND** the client supplies verified account-neutral full history
- **WHEN** local selection rejects the owner with `account_usage_limit_reached`
- **THEN** the service removes owner affinity and continuity anchors from the projected replay
- **AND** it excludes the usage-limited owner and selects another eligible account

#### Scenario: Unsafe history remains on the owner

- **GIVEN** an HTTP-bridge continuation is durably owned by one account
- **AND** the supplied history is not safe for fresh cross-account replay
- **WHEN** local selection rejects the owner with `account_usage_limit_reached`
- **THEN** the service returns that rejection without moving the continuation to another account

### Requirement: Account-neutral current input may outlive a stale owner anchor

When an unavailable owner prevents an HTTP-bridge resume and verified full
history is not available, the service MAY remove the stale previous-response
anchor and replay only the remaining current input if that input is independently
account-neutral. This best-effort path MUST exclude the unavailable owner and
MUST NOT replay account-scoped files, conversation IDs, orphaned tool outputs,
or response-owned items. An owner bridge that closes with `stream_incomplete`
before emitting any response event MAY be treated as unavailable for this path.
The service MUST attempt that eventless-disconnect replay at most once per
request and MUST NOT use it after downstream-visible output.

For a request carrying a Codex thread identifier, if the exact fresh replay is
unsafe, the service MAY project the complete client-supplied history by removing
known response-owned bookkeeping. If that projection remains unsafe, the
service MAY replay only the newest portable user text. Both lossy paths MUST add
an honest continuity notice containing the percent-encoded
`codex://threads/<thread-id>` deeplink, MUST exclude the failed owner, and MUST
omit account-scoped files, encrypted reasoning, response IDs, orphaned tool
state, and other nonportable items. Requests without a Codex thread identifier
MUST retain the existing fail-closed behavior.

When a mixed Responses-Lite `additional_tools` bundle prevents the sanitized
history from moving accounts, the projection MUST retain every independently
account-neutral tool declaration and omit only declarations that remain
account-scoped or unsupported. After a replacement account is selected, the
service MUST persist that account on the original durable task row before
streaming the replacement response. If the failed transport already released
the row, that update MUST require the original owner epoch, original account,
closed state, and empty continuity anchors so a concurrent successor cannot be
overwritten.

#### Scenario: Plain resume continues without old context

- **GIVEN** a resume contains a stale owner-bound previous-response anchor
- **AND** its remaining input is a plain user message
- **WHEN** the owner is unavailable
- **THEN** the service removes the stale anchor and selects another account
- **AND** the replacement receives the current message without a promise that old context was retained

#### Scenario: Owner-scoped current input remains blocked

- **GIVEN** a resume contains a stale owner-bound previous-response anchor
- **AND** its remaining input contains account-scoped or structurally incomplete items
- **WHEN** the owner is unavailable
- **THEN** the service does not move those account-scoped items to another account
- **AND** without a Codex thread identifier it does not move the request at all

#### Scenario: Codex thread resumes with sanitized history

- **GIVEN** a Codex thread resume supplies full history containing removable response-owned bookkeeping
- **WHEN** the owner is unavailable and the projected history is account-neutral
- **THEN** the service selects another account with the maximum portable projected history
- **AND** it identifies the original task in an honest continuity notice

#### Scenario: Sanitized history retains portable Desktop tools

- **GIVEN** a Codex thread resume contains a mixed Responses-Lite tool bundle
- **AND** some declarations are account-neutral while others are not portable
- **WHEN** sanitized history is selected on another account
- **THEN** the replacement receives the account-neutral tool declarations
- **AND** the nonportable declarations are omitted without discarding the portable tools or conversation history

#### Scenario: Released task row follows the replacement account

- **GIVEN** the failed owner bridge released its durable task row before best-effort replay selected a replacement
- **AND** the row still has the original owner epoch and account with no continuity anchors
- **WHEN** the replacement account is selected
- **THEN** the service updates the closed row to that replacement account before response streaming
- **AND** a claimed, re-anchored, or otherwise concurrently changed row is fenced from that update

#### Scenario: Codex thread falls back to its newest portable message

- **GIVEN** a Codex thread resume contains history that remains unsafe after projection
- **AND** its newest user message contains portable text
- **WHEN** the owner is unavailable
- **THEN** the service drops the unsafe history and sends only that portable text to another account
- **AND** the continuity notice includes the original `codex://threads/<thread-id>` deeplink and states that history was not transferred

#### Scenario: Eventless owner disconnect switches once

- **GIVEN** a resume contains an owner-bound previous-response anchor and a plain current user message
- **AND** the owner bridge closes with `stream_incomplete` before emitting a response event
- **WHEN** another account is eligible
- **THEN** the service removes the stale anchor, excludes the failed owner, and replays the current message once
- **AND** a failure of that replacement does not trigger another server-side replay
