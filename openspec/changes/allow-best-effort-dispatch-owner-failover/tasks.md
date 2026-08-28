## 1. Specification

- [x] Define the narrow best-effort replay exception.
- [x] Validate the change in strict mode.

## 2. Implementation

- [x] Release dispatch-only payload ownership after a pre-visible failover decision.
- [x] Preserve every pre-existing hard account-ownership constraint.
- [x] Cover nonportable image history, account failover, and sticky re-anchoring.
- [x] Route a usage-limited durable owner through verified account-neutral full resend.
- [x] Cover safe and unsafe full-history replay after a local usage-limit rejection.
- [x] Resume account-neutral current input without an unavailable owner's stale anchor.
- [x] Retry that current input once after an eventless owner-bridge disconnect.
- [x] Preserve projected Codex thread history or fall back to a deeplink plus the newest portable message.

## 3. Verification

- [x] Run the focused proxy regression, Ruff, and `git diff --check`.
