## ADDED Requirements

### Requirement: Bridge usage authorization follows dispatch preparation

Before sending a newly admitted HTTP bridge turn or synthetic bridge prewarm, the system MUST re-evaluate the pinned account's usage policy after waits for serialized dispatch and durable continuity preparation. A blocking policy MUST reject the unsent work with `account_usage_limit_reached`, release its admission resources, and preserve already-dispatched responses. Authorization reads MUST NOT hold the pending-response lock.

#### Scenario: A policy changes while a bridge turn waits for dispatch
- **GIVEN** a bridge turn passed queue and response-create admission
- **WHEN** its account becomes usage-limited while it waits for serialized dispatch
- **THEN** the turn fails with `account_usage_limit_reached` without being sent upstream
- **AND** its queue, waiter, and lease accounting are released

#### Scenario: A policy changes during durable continuity preparation
- **GIVEN** an unsent bridge turn requires durable continuity preparation
- **WHEN** its account becomes usage-limited during that preparation
- **THEN** the turn fails with `account_usage_limit_reached` before upstream dispatch
- **AND** already-dispatched turns retain their ownership and settlement paths

#### Scenario: A policy changes while prewarm waits for dispatch
- **WHEN** a bridge prewarm's account becomes usage-limited while the prewarm waits for serialized dispatch
- **THEN** the prewarm is not sent upstream
- **AND** its admission resources are released

### Requirement: Sticky admission observes policy changes during persistence

If account-selection data is invalidated during affinity persistence, selection MUST NOT return the previously authorized account or retain its provisional concurrency lease. It MUST fail closed with `selection_state_changed` so a subsequent request can reload policy, while preserving established continuity ownership.

#### Scenario: Usage crosses a cap while affinity is persisted
- **GIVEN** an account was selected from an available usage observation
- **WHEN** a committed observation crosses its cap and invalidates selection data during affinity persistence
- **THEN** admission returns `selection_state_changed` without an account or lease
- **AND** its concurrency accounting is released

### Requirement: Empty successful usage polls supersede capped-account measurements

When a successful usage poll provides no standard quota windows for an account with an enabled usage policy, the system MUST supersede older standard observations with unavailable data and invalidate selection data. It MUST NOT continue authorizing that account from the older measurements. Accounts without an enabled policy MUST retain the existing additional-only poll behavior.

#### Scenario: A capped account loses standard telemetry
- **GIVEN** an enabled policy has fresh standard observations below its cap
- **WHEN** a successful poll omits the standard rate-limit object or returns no standard windows
- **THEN** the dashboard reports `data_unavailable`
- **AND** account selection rejects it with `account_usage_limit_reached`

#### Scenario: An uncapped account has an additional-only poll
- **WHEN** an account without an enabled usage policy receives a successful poll with no standard windows
- **THEN** the poll retains the established standard-observation persistence behavior
