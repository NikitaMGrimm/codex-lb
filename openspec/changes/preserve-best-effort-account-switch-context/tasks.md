## 1. Portable replay projection

- [x] 1.1 Normalize known Codex Desktop metadata during account-neutral replay
      projection while leaving unknown metadata fail-closed.
- [x] 1.2 Remove blank text fragments from otherwise complete direct-tool
      outputs without discarding substantive output.

## 2. Recovery continuity

- [x] 2.1 Preserve explicit top-level tool controls and the portable
      Responses-Lite tool/developer prefix in newest-message recovery.
- [x] 2.2 Rebind the original locally owned durable task to the successful
      replacement account with owner-epoch and anchor fencing.
- [x] 2.3 Log rejected replay stages, the selected stage, and rebind outcome.

## 3. Regression coverage

- [x] 3.1 Cover current Desktop metadata and empty tool-output fragments.
- [x] 3.2 Cover both sanitized-history and latest-message tool preservation.
- [x] 3.3 Cover durable task rebinding and structured recovery diagnostics.

## 4. Validation

- [x] 4.1 Run focused replay-safety and HTTP bridge tests.
- [x] 4.2 Run lint, type, architecture, and strict OpenSpec checks.
- [x] 4.3 Verify both captured production task histories classify as portable.
