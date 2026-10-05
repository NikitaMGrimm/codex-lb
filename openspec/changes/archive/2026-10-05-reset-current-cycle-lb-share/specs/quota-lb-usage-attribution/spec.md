## MODIFIED Requirements

### Requirement: Credit-scaled LB share estimate
The dashboard API SHALL estimate Codex LB's share of an eligible account's current weekly or monthly quota cycle. It MUST use only successful LB request costs assigned to that account since the current cycle boundary and the latest observed used percentage, including a nonzero first observation. A previous 100%-used observation MUST NOT be required. It SHALL support positive maintained long-window subscription-credit capacities and the configured Pro ratio. At zero observed use and zero logged cost it SHALL report zero immediately. If observed use is zero but logged cost is positive, it SHALL wait for a positive quota observation instead of inventing a percentage.

#### Scenario: New cycle first observed at five percent
- **GIVEN** a fresh reset deadline confirms a new cycle whose first observed usage is 5%
- **WHEN** the dashboard requests attribution
- **THEN** all 5% contributes to observed use and only current-cycle LB costs contribute
- **AND** prior-cycle usage and LB costs do not carry forward

### Requirement: Operator Pro ratio
Dashboard settings SHALL allow an optional positive Pro weekly capacity ratio relative to Plus/Team weekly capacity. When unset, attribution SHALL use the maintained Pro weekly subscription-credit capacity. When set, attribution SHALL use the configured ratio for Pro weekly observations, including calibration references. The setting MUST NOT change routing or displayed Subscription credits.

#### Scenario: Pro weekly ratio is twenty
- **WHEN** Plus weekly capacity is 7,560 credits and the Pro ratio is 20
- **THEN** attribution uses 151,200 credits without changing routing or displayed Subscription capacity

### Requirement: Dashboard displays the estimate beside its quota
The dashboard SHALL show available estimates beside the matching weekly/monthly quota in card and list views, with the cycle's date range available in the explanation. It MUST NOT imply attribution to an individual. Missing estimates SHALL show an unavailable state explaining fresh cycle data, positive quota use, and peer calibration requirements. An API error MUST NOT be presented as an account-specific unavailable estimate. Expired estimates MUST NOT remain visible beside a renewed quota while attribution refresh is pending.

#### Scenario: Cached estimate belongs to an expired or replaced cycle
- **WHEN** fresh quota data confirms a renewal before the attribution query returns
- **THEN** the previous-cycle badge is hidden and the unavailable state is displayed

### Requirement: Attribution access and query bounds
The API SHALL require the same account-read permission as dashboard overview and SHALL bound history reads to the preceding 30 days. Dashboard overview polling MUST NOT trigger attribution calculation.

#### Scenario: Viewer lacks account-read permission
- **WHEN** a user without account-read permission requests attribution
- **THEN** the API denies access

## ADDED Requirements

### Requirement: Fresh quota reset detection
The API SHALL recognize a reset when a fresh long-window reset deadline advances by at least one day, independently of whether used percentage decreases. It SHALL also recognize renewed deadlines after the previous deadline expires, renewed deadlines whose inferred start falls between observations, and fresh meaningful drops to zero even before reset metadata refreshes. Small same-cycle percentage corrections, including a one-point correction to zero with the same future deadline, MUST NOT reset the accounting window. Expired or regressed reset deadlines MUST NOT restore an old-cycle estimate. Natural reset boundaries SHALL use the previous reset deadline; early resets SHALL use the new deadline minus the quota duration when that boundary fits between surrounding observations or a deadline advance of at least one day confirms renewal despite an intervening stale poll; otherwise the first fresh reset observation. An initial current cycle SHALL be inferred from its fresh reset deadline when no reset transition is retained.

#### Scenario: Equal or higher usage after reset
- **GIVEN** a new fresh deadline and a first reading equal to or higher than the previous cycle's final reading
- **THEN** the API starts a new accounting cycle and includes the entire new reading

#### Scenario: Expired quota awaiting refresh
- **GIVEN** the latest quota deadline has expired or a latest observation regresses to an old reset deadline
- **THEN** attribution is unavailable until fresh current-cycle data arrives

### Requirement: Bounded recent peer calibration
The API SHALL calibrate estimated USD cost per subscription credit from other eligible accounts' recent observed quota growth and successful LB costs over matching peer observation intervals, bounded to the preceding 30 days. Calibration SHALL count nonzero first observations after resets, including resets with equal or higher usage. A single reference account with positive growth and cost SHALL suffice; there SHALL be no minimum 20-point growth requirement. The API SHALL omit a positive-use estimate when no positive peer calibration is available. Calibration evidence MAY span earlier quota cycles; target accounting MUST remain restricted to the current cycle.

#### Scenario: Early estimate from a small peer sample
- **GIVEN** one peer has positive observed growth below 20 percentage points and positive logged cost
- **THEN** the API can produce a current-cycle estimate without waiting for another reference or more growth

### Requirement: Uncapped diagnostic estimates
The API and dashboard SHALL retain finite nonnegative estimated shares above 100% without hiding or clamping them. The UI SHALL label the result as approximate and explain that values above 100% indicate calibration mismatch, not measured upstream attribution. The estimate SHALL include cycle-start and observation timestamps, observed credits, estimated LB credits, and reference count.

#### Scenario: Estimate is 140 percent
- **WHEN** calibration implies an LB share of 140%
- **THEN** the API reports 140% and card/list quota indicators display approximately 140% via LB
