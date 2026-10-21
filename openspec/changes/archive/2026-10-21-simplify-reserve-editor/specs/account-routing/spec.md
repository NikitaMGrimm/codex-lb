## MODIFIED Requirements

### Requirement: Reserve-oriented editing
The editor SHALL ask how much quota to keep for direct use, converting reserve percentages to the existing maximum-used API contract. Zero reserve SHALL map to 100 percent maximum-used; the input's declared maximum MUST exclude 100 percent reserve because the API requires a positive maximum-used value. The editor SHALL show one row per reported 5-hour or weekly window, holding the reserve that applies to that window: its override, otherwise the default. It SHALL add one row for the default when window telemetry is unknown or no standard window is reported (labeled All windows, or Monthly for a monthly-only account), or when a monthly, nonstandard, or unidentified window is reported alongside a standard window (labeled Other windows). The editor MUST NOT offer a 5-hour or weekly row when that window is absent, and monthly usage MUST NOT use a weekly override.
Each row SHALL show provider remaining and the quota Codex LB could still use with the unsaved reserve, and SHALL mark a window as reached before saving when its remaining quota is at or below the reserve. A disabled policy SHALL show the full remaining quota as usable.
A blank row SHALL mean no reserve. On save, a standard row equal to the default it would inherit SHALL clear its override; any other value SHALL be stored as that window's override. When no default row is shown, the stored default MUST be retained. Hiding an inapplicable override MUST preserve its saved value when another row is edited. Saving with no reserve in every shown row SHALL remove the policy. Save and Cancel SHALL appear only while the draft differs from the saved policy, and Escape SHALL discard the draft; a saved policy with no reserve in any shown row SHALL instead offer removal without an edit. Validation SHALL apply only to edited rows so an untouched row keeps its exact saved value. The enable switch SHALL be visible in every state, SHALL be unavailable until a policy is saved, and SHALL apply immediately. Saving a new policy SHALL enable it. The editor SHALL label an enabled policy in state `reached` or `data_unavailable` with `Limit reached` or `Usage unavailable` and SHALL NOT show a separate active-state badge.
Bars SHALL place reserved quota on the left, usable quota next, and consumed quota on the right. Stripes SHALL not exceed provider remaining.

#### Scenario: Twenty percent reserve
- **WHEN** the operator saves a 20 percent reserve and usage is 54 percent
- **THEN** the maximum-used API value SHALL be 80
- **AND** the bar SHALL show 20 percent striped on the left, 26 percent usable next, and 54 percent consumed on the right.

#### Scenario: Unsaved reserve previews a blocked window
- **GIVEN** an enabled policy and a 5-hour window with 35 percent remaining
- **WHEN** the operator types a 40 percent 5-hour reserve without saving
- **THEN** the 5-hour row SHALL show 0 percent usable and mark the window as reached.

#### Scenario: Rows show effective reserves
- **GIVEN** a default of 80, a 5-hour override of 70, and a weekly override of 90 on an account reporting 5-hour and weekly windows
- **THEN** the editor SHALL show a 30 percent 5-hour reserve and a 10 percent weekly reserve and no default row
- **WHEN** the operator changes the weekly reserve to 15 and saves
- **THEN** the update SHALL set the 5-hour override to 70 and the weekly override to 85 without changing the default.

#### Scenario: Window matching the default keeps inheriting
- **GIVEN** a default of 80 and no overrides on an account reporting 5-hour and weekly windows
- **WHEN** the operator changes only the 5-hour reserve to 30 and saves
- **THEN** the update SHALL set the 5-hour override to 70 and clear the weekly override.

#### Scenario: Clearing every row removes the policy
- **WHEN** the operator clears every shown reserve of a saved policy and saves
- **THEN** the policy SHALL be removed and disabled.

#### Scenario: Policy left with only an unreported-window override
- **GIVEN** an enabled policy whose only value is a 5-hour override on an account that reports only a weekly window
- **THEN** the editor SHALL offer removal without an edit
- **AND** removing it SHALL clear every value and disable the policy.

#### Scenario: Reserve controls follow reported windows
- **GIVEN** an account reports only a weekly standard window
- **THEN** the editor SHALL offer only a weekly row, and saving it SHALL retain the stored default and any hidden 5-hour override.
- **GIVEN** an account reports only a monthly standard window
- **THEN** the editor SHALL offer a Monthly row backed by the default without 5-hour or weekly rows.
- **WHEN** the operator saves, disables, or re-enables that policy
- **THEN** the monthly effective limit SHALL retain the same default-policy semantics.

#### Scenario: Nonstandard windows do not offer standard overrides
- **WHEN** reported windows have durations other than 300 or 10080 minutes
- **THEN** the editor SHALL offer only an All windows row for the default
- **AND** a 10080-minute window in either reported slot SHALL offer a weekly row.
