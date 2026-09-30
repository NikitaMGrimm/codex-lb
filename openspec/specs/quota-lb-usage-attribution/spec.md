## Purpose

Define the dashboard's estimate of long-window quota use routed through Codex LB.

## Requirements

### Requirement: Credit-scaled LB share estimate
The dashboard API SHALL estimate Codex LB's share of an eligible account's observed long-window quota use since its latest 100% observation in the preceding 30 days. It MUST support weekly windows for all account plans with a positive weekly subscription-credit capacity and monthly windows for plans with a positive monthly capacity. It MUST count usage across subsequent resets, use only successful request logs assigned to the account for LB cost, and convert observed percentage growth with Codex LB's maintained capacity for the account's plan and window. It MUST calibrate USD cost per subscription credit from at least two other eligible accounts over the same interval. The reported share MUST be between 0% and 100% and MUST include observation timestamps and observed credit use.

#### Scenario: Usage spans multiple resets
- **GIVEN** an eligible account was observed at 100%, then consumed 55%, reset, consumed 99%, reset, and consumed 6%
- **WHEN** the dashboard requests its LB share estimate
- **THEN** observed use is 160 percentage points converted with that account's long-window credit capacity
- **AND** only successful LB request costs after the 100% observation contribute to estimated LB use

#### Scenario: Missing or inconsistent evidence
- **WHEN** the account has no 100% observation within 30 days, a stale current long-window observation, fewer than two usable references, no positive observed use, or an implied LB contribution exceeding observed use
- **THEN** the API omits its estimate

### Requirement: Operator Pro ratio
Dashboard settings SHALL allow an optional positive Pro weekly capacity ratio relative to Plus/Team weekly capacity. When unset, attribution SHALL use the maintained Pro weekly subscription-credit capacity. When set, attribution SHALL use the configured ratio for Pro weekly observations, including when Pro is a calibration reference. The setting MUST NOT change routing or displayed Subscription credits.

#### Scenario: Pro weekly ratio is set to twenty
- **WHEN** Plus/Team weekly capacity is 7,560 credits and the operator sets the Pro ratio to 20
- **THEN** attribution uses 151,200 credits as the effective Pro weekly capacity
- **AND** the dashboard continues to display the maintained Pro Subscription capacity

### Requirement: Dashboard displays the estimate beside its quota
The main dashboard SHALL display an available estimate beside the corresponding account's weekly or monthly quota in both card and list views, labeled as approximate usage “via LB.” It MUST NOT imply that LB use identifies an individual person. After a successful attribution response, accounts without an estimate SHALL display a compact unavailable state next to the corresponding long-window quota with an explanation of the data requirements and inconsistent-calibration guard. An attribution API error MUST NOT be presented as an account-specific unavailable estimate.

#### Scenario: Estimate is available
- **WHEN** the dashboard displays an account with a 60% LB share estimate
- **THEN** its corresponding long-window quota area shows an approximately 60% “via LB” indicator in both layouts

#### Scenario: Estimate is unavailable
- **WHEN** the attribution API succeeds but omits an account's estimate
- **THEN** that account's long-window quota area shows a compact unavailable indicator in both layouts
- **AND** its explanation describes the evidence and calibration requirements without reporting an invalid percentage

### Requirement: Attribution access and query bounds
The attribution API SHALL require the same account-read permission as the dashboard overview and MUST bound usage-history reads to the preceding 30 days. Dashboard polling for other overview data MUST NOT trigger attribution calculation.

#### Scenario: Viewer lacks account-read permission
- **WHEN** a user without account-read permission requests attribution
- **THEN** the API denies access
