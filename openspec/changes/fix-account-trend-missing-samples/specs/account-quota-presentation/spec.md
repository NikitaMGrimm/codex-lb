## ADDED Requirements

### Requirement: Faithful account trend series
The account trend chart SHALL preserve every provided observation timestamp and SHALL represent an absent window sample as a gap rather than zero remaining. Legends SHALL list only available series. Monthly-account long-window tooltips SHALL use monthly labels.

#### Scenario: Different observation timestamps
- **GIVEN** a primary observation and a monthly observation have different timestamps
- **WHEN** the chart combines the series
- **THEN** both observations SHALL be retained and the missing counterpart SHALL remain absent rather than zero.

#### Scenario: Monthly-only trend
- **GIVEN** only monthly observations exist
- **THEN** the chart SHALL show Monthly without a 5-hour legend and SHALL label its long-window tooltip Monthly.

### Requirement: Account-scoped quota presentation state
Smoothed quota values and known-window state SHALL reset when the selected account changes.

#### Scenario: Switching quota shapes
- **GIVEN** a dual-window account was selected
- **WHEN** the operator selects a different monthly-only account
- **THEN** only the new account's monthly quota SHALL be shown, without retained 5-hour or weekly values.
