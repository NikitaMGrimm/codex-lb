## Context

The previous draft hard-coded 20:1 and only handled Pro weekly quota. Codex LB's maintained weekly capacities currently imply 6.67:1, which makes that calibration exceed observed Pro use. Request logs contain USD cost, not per-request subscription credits, so the result must remain an estimate.

## Decisions

1. Keep attribution in a separately fetched, account-read-protected endpoint. Poll once per minute to avoid adding history scans to ordinary dashboard refreshes.
2. Use the latest 100% observation in the preceding 30 days for each account's displayed long quota window. Count high-water usage growth across resets. Convert percentage points to credits with the maintained capacity for that plan and window.
3. For a target, calibrate successful logged USD cost against observed credit growth on at least two other eligible accounts over the same interval. The Pro override, when set, substitutes Plus/Team weekly capacity multiplied by the configured ratio; it affects attribution only, not routing or the Subscription display.
4. Omit an estimate if its baseline or recent sample is missing, calibration is sparse, or implied LB credits exceed observed credits. Do not clamp inconsistent estimates.
5. Keep the indicator small and label it approximate. The tooltip states the calibration assumption and that it cannot identify a person.

## Limits

Direct usage on reference accounts and different request mixes can bias USD-per-credit calibration. A configured capacity ratio corrects that one assumption; it does not reveal direct use or turn request cost into measured subscription credits. Unsupported and inconsistent cases have no displayed percentage.
