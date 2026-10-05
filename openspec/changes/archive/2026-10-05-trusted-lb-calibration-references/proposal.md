## Why

Calibrating against accounts with unknown external use attributes that external consumption to LB. Two owner-confirmed clean references predict each other's current-cycle consumption within about one percentage point, while the existing estimator reports more than 225%.

## What Changes

- Select trusted LB-only reference accounts in attribution settings.
- Calibrate against each selected peer's fresh current quota cycle and matching logged cost; exclude the target itself.
- Preserve reset handling, configured Pro capacity ratios, immediate estimates, and values above 100%.
- Store the reference selection in one additive settings column, initially empty.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `quota-lb-usage-attribution`: explicit trusted references and current-cycle peer calibration.

## Impact

Dashboard settings/API, attribution service, settings UI, and one additive migration. No dependencies or routing changes. The authorized rollout selects the two clean Team accounts after deployment.
