## Why

Quota bars combine traffic sent through Codex LB with direct OpenAI use. The operator needs a bounded, explicitly approximate LB share for any account with a supported long quota window, and a way to correct the Pro-to-Plus weekly capacity ratio when maintained subscription-credit capacities differ from the operator's intended ratio.

## What Changes

- Estimate LB share since the latest observed 100% long-window quota reading, using successful LB request costs and observed subscription-credit consumption for calibration.
- Support accounts with weekly quota windows and Free accounts with monthly windows. Derive capacities from Codex LB's subscription-credit values.
- Add an optional dashboard setting for Pro weekly capacity relative to Plus/Team weekly capacity. When unset, use the maintained credit capacities; setting it to 20 uses a 20:1 ratio.
- Show a compact approximate share beside the corresponding quota in both account layouts. Omit inconsistent or unsupported estimates.

## Impact

Dashboard API and settings, quota-history reads, one additive database migration, dashboard UI, tests, and OpenSpec.
