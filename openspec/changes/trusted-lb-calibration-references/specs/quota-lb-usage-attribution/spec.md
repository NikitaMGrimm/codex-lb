## MODIFIED Requirements

### Requirement: Bounded recent peer calibration

The API SHALL calibrate estimated USD cost per subscription credit only from explicitly selected trusted LB-only accounts. It MUST exclude the target account from its own calibration. Each reference SHALL contribute its latest observed current-cycle used percentage, including a nonzero first reading, and successful LB costs over that same cycle through the quota observation. Expired, stale, regressed, or undefined reference cycles MUST NOT contribute. A single selected reference with positive use and cost SHALL suffice; there SHALL be no minimum usage threshold. History SHALL remain bounded to 30 days. Positive-cost estimates without a usable trusted peer SHALL be omitted; zero-cost estimates SHALL remain available without peers.

#### Scenario: Unknown Pro use cannot inflate Team estimates
- **GIVEN** two Team accounts are selected as clean references and Pro is not selected
- **WHEN** Pro consumes quota outside LB
- **THEN** Pro consumption does not contribute to calibration
- **AND** each Team target is calibrated from the other selected Team account

#### Scenario: First small reference reading
- **GIVEN** one trusted peer first reports 1% used with positive current-cycle LB cost
- **THEN** it supplies calibration immediately without waiting for previous cycles

#### Scenario: Early estimate from a small peer sample
- **GIVEN** one selected trusted peer has positive observed usage below 20 percentage points and positive logged cost
- **THEN** the API can produce a current-cycle estimate without waiting for another reference or more usage

## ADDED Requirements

### Requirement: Trusted reference selection

Dashboard settings SHALL persist a bounded list of trusted reference account IDs, initially empty. Administrators SHALL select and deselect reference accounts in the LB attribution settings. Unrelated settings saves MUST preserve that selection, and reference selection MUST preserve the configured Pro ratio. The UI explanation SHALL identify references as LB-only accounts and their selection as an assumption.

#### Scenario: Select two clean accounts
- **WHEN** an administrator saves two account IDs as trusted references
- **THEN** attribution uses only those references after settings cache invalidation
- **AND** the existing Pro ratio remains unchanged
