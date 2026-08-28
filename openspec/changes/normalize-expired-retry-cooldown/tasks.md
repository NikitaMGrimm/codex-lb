## 1. Specification

- [x] Add the expired-cooldown, future-cooldown, and observed-transition requirements.
- [x] Validate the change in strict mode.

## 2. Implementation

- [x] Normalize non-positive durable cooldown remaining time to the zero
      sentinel on first observation while preserving future deadlines.
- [x] Preserve one-probe half-open admission for an episode observed cooling
      and clear leftover leases from replacement episodes.
- [x] Add regression coverage for first-observed expiry, observed transitions,
      equal-version probe retention, and replacement-episode cleanup.

## 3. Verification

- [x] Run focused retry-circuit tests, Ruff, and `git diff --check`.
