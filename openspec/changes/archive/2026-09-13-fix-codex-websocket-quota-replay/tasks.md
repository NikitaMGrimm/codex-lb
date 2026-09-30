## Investigation
- [x] Match T3 backend errors to live LB request logs.
- [x] Identify exact deployed revision and isolate a detached checkout.
- [x] Capture both installed Codex backend builds against a local fake endpoint using copied history.
- [x] Reproduce same-account quota replay through the WebSocket service with synthetic data.
- [x] Separate proven compatibility defects from the unproven client-frequency explanation.

## Implementation and release criteria
- [x] Add narrowly validated support for known metadata and reasoning context.
- [x] Preserve a safe complete replay body and exclude the failed account on portable pre-created quota errors.
- [x] Cover full-history inline tools and owned IDs using the existing projection contract.
- [x] Assert supplied tool call/result preservation and refuse replay after output or acceptance; this does not guarantee model behavior after replay.
- [x] Keep file ownership, unknown shapes, missing history, and visible-output cases fail-closed.
- [x] Add metadata-only replay-refusal diagnostics.
- [x] Run WebSocket and HTTP bridge regression checks, lint and strict OpenSpec validation.
- [x] Review the production-targeted patch and existing custom deployment changes.
- [x] Prepare the separate operator deployment handoff; do not deploy from this session.

## Operator follow-up (outside this implementation)
Deploy through the prepared PowerShell command, then verify a live T3 account-limit transition. Do not claim live resolution before that check.
