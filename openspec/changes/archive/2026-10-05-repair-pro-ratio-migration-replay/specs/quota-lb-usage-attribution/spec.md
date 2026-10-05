## ADDED Requirements

### Requirement: Missing metadata does not reopen an old quota cycle

The system MUST retain the last confirmed current-cycle reset deadline when
a later reading omits reset metadata. It MUST reject a regressed deadline
even if the immediately preceding reading omitted its deadline. The retained
deadline MUST expire the estimate at the API and be exposed to the UI. A
renewed deadline after a metadata gap MUST still establish the new cycle.

#### Scenario: Old deadline follows a metadata gap

- **GIVEN** a renewed deadline established the current quota cycle
- **AND** a subsequent reading omits its deadline
- **WHEN** an old deadline is replayed
- **THEN** that reading is rejected as stale
- **AND** a later missing-deadline reading still retains the confirmed deadline

#### Scenario: An estimate expires during a metadata gap

- **GIVEN** the latest quota reading is recent and omits reset metadata
- **AND** the last confirmed cycle deadline has passed
- **WHEN** the dashboard requests LB attribution
- **THEN** the old-cycle estimate is omitted until a fresh cycle is established

## MODIFIED Requirements

### Requirement: Credit-scaled LB share estimate
The dashboard API SHALL estimate Codex LB's share of an eligible account's current weekly or monthly quota cycle. It MUST use only successful LB request costs assigned to that account since the current cycle boundary and the latest observed used percentage, including a nonzero first observation. A previous 100%-used observation MUST NOT be required. It SHALL support positive maintained long-window subscription-credit capacities and the configured Pro ratio. At zero logged LB cost it SHALL report zero immediately without requiring peer calibration, including when observed use is positive. If observed use is zero but logged cost is positive, it SHALL wait for a positive quota observation instead of inventing a percentage.

#### Scenario: New cycle first observed at five percent
- **GIVEN** a fresh reset deadline confirms a new cycle whose first observed usage is 5%
- **WHEN** the dashboard requests attribution
- **THEN** all 5% contributes to observed use and only current-cycle LB costs contribute
- **AND** prior-cycle usage and LB costs do not carry forward
### Requirement: Bounded recent peer calibration
The API SHALL calibrate estimated USD cost per subscription credit from other eligible accounts' recent observed quota growth and successful LB costs over matching peer observation intervals, bounded to the preceding 30 days. Calibration SHALL count nonzero first observations after resets, including resets with equal or higher usage. A single reference account with positive growth and cost SHALL suffice; there SHALL be no minimum 20-point growth requirement. The API SHALL omit an estimate with positive logged LB cost when no positive peer calibration is available. Calibration evidence MAY span earlier quota cycles; target accounting MUST remain restricted to the current cycle.

#### Scenario: Early estimate from a small peer sample
- **GIVEN** one peer has positive observed growth below 20 percentage points and positive logged cost
- **THEN** the API can produce a current-cycle estimate without waiting for another reference or more growth
