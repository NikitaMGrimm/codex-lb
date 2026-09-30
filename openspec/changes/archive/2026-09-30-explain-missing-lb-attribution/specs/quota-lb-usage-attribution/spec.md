## MODIFIED Requirements

### Requirement: Dashboard displays the estimate beside its quota

The main dashboard SHALL display an available estimate beside the corresponding account's weekly or monthly quota in both card and list views, labeled as approximate usage “via LB.” It MUST NOT imply that LB use identifies an individual person. After a successful attribution response, accounts without an estimate SHALL display a compact unavailable state next to the corresponding long-window quota with an explanation of the data requirements and inconsistent-calibration guard. An attribution API error MUST NOT be presented as an account-specific unavailable estimate.

#### Scenario: Estimate is available

- **WHEN** the dashboard displays an account with a 60% LB share estimate
- **THEN** its corresponding long-window quota area shows an approximately 60% “via LB” indicator in both layouts

#### Scenario: Estimate is unavailable

- **WHEN** the attribution API succeeds but omits an account's estimate
- **THEN** that account's long-window quota area shows a compact unavailable indicator in both layouts
- **AND** its explanation describes the evidence and calibration requirements without reporting an invalid percentage
