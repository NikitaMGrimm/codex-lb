# responses-api-compat Delta

## ADDED Requirements

### Requirement: Expired durable retry cooldowns do not create false half-open transitions

When a durable retry-circuit row is first observed with an absent or elapsed
cooldown, the proxy MUST load the in-memory cooldown deadline as zero. It MUST
NOT interpret that first observation as a cooldown that just ended, consume an
exclusive half-open probe lease, or suppress subsequent requests solely because
the persisted cooldown elapsed. If the same durable episode was previously
observed with an active cooldown, its later expiry MUST admit exactly one fresh
half-open probe and MUST retain that episode's active probe lease across
equal-version durable reloads. A future cooldown or a replacement durable
episode MUST clear any leftover probe lease from the prior state. Future
cooldown deadlines MUST remain represented as a positive in-memory deadline,
with thresholds, backoff, persistence, ownership, and retry classification
unchanged.

#### Scenario: Elapsed cooldown reloads open without a probe lease

- **GIVEN** a hard-affinity durable retry row whose cooldown deadline is in the past
- **WHEN** retry admission loads the row
- **THEN** the in-memory cooldown deadline is zero
- **AND** the half-open lease is zero
- **AND** repeated admission checks remain allowed

#### Scenario: Future cooldown remains enforced

- **GIVEN** a hard-affinity durable retry row whose cooldown deadline is in the future
- **WHEN** retry admission loads the row
- **THEN** the positive cooldown remains enforced until it expires

#### Scenario: Observed cooldown expiry admits one fresh probe

- **GIVEN** a worker previously loaded a hard-affinity durable retry row while its cooldown was active
- **WHEN** the same durable episode is reloaded after that cooldown expires
- **THEN** exactly one request is admitted as the half-open probe
- **AND** the worker suppresses later non-bypassed requests while that probe lease remains active

#### Scenario: Replacement episode drops a stale probe lease

- **GIVEN** a worker retains a half-open lease from an earlier retry episode
- **WHEN** it adopts a different durable episode
- **THEN** the earlier episode's probe lease is cleared
