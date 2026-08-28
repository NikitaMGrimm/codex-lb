## 1. Specification

- [x] Define the narrow best-effort replay exception.
- [ ] Validate the change in strict mode.

## 2. Implementation

- [x] Release dispatch-only payload ownership after a pre-visible failover decision.
- [x] Preserve every pre-existing hard account-ownership constraint.
- [x] Cover nonportable image history, account failover, and sticky re-anchoring.

## 3. Verification

- [x] Run the focused proxy regression, Ruff, and `git diff --check`.
