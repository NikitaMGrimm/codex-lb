## ADDED Requirements

### Requirement: Pro attribution migration replay preserves an existing compatible column

The locked application migration runner MUST inspect the existing
`dashboard_settings.pro_weekly_capacity_multiplier` column when it reaches
`20260930_000000_pro_weekly_attribution_ratio`. If that nullable floating-point
column already exists without a server default, the runner MUST preserve its
values and advance only that migration step without repeating its DDL. Other
pending revisions MUST execute through Alembic's original plan. Published
migration contents, ancestry, and downgrade behavior MUST remain unchanged.
A missing column MUST be created through the published migration. An existing
incompatible column MUST fail before the Pro ratio step is stamped.

#### Scenario: A rewound or missing ledger does not re-add the column

- **GIVEN** a database already has a compatible Pro ratio column and stored ratio
- **AND** recovery has rewound or lost its Alembic ledger
- **WHEN** the locked migration runner upgrades to head
- **THEN** the upgrade completes without a duplicate-column error
- **AND** the stored ratio and surviving dashboard credentials are preserved
- **AND** other pending revisions run normally

#### Scenario: A partial schema still applies unrelated migrations

- **GIVEN** the compatible Pro ratio column exists on a database missing other
  pending schema changes
- **WHEN** the locked migration runner upgrades to head
- **THEN** only the Pro ratio DDL is skipped
- **AND** the missing schema changes are applied

#### Scenario: A fresh upgrade applies the published revision

- **GIVEN** the Pro ratio column is absent
- **WHEN** the locked migration runner reaches its revision
- **THEN** the published DDL creates the column normally

#### Scenario: An incompatible existing column fails closed

- **GIVEN** the existing Pro ratio column has an incompatible type, nullability,
  or server default
- **WHEN** the locked migration runner reaches its revision
- **THEN** it fails with guidance on the schema mismatch
- **AND** that migration step remains unstamped

#### Scenario: Target forms preserve their original migration plan

- **WHEN** an upgrade uses a full revision, an unambiguous prefix, or a relative
  target that reaches the already-applied Pro ratio column
- **THEN** the runner reaches exactly the requested target
- **AND** it skips only the already-applied Pro ratio DDL
