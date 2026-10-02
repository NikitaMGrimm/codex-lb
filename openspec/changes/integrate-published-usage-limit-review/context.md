# Published/local usage-limit integration

The published head adds independent default, 5-hour, and weekly reserve controls. Integration retains those controls and both commit histories, together with the local final-dispatch and sticky-persistence fences. No new service, configuration, or dependency is introduced.

## Contract decisions

The published policy-denial contract is HTTP 429 / `rate_limit_error`, without an upstream reset deadline. Direct Responses requests use the canonical selection-error mapper, preserving the local correction to the earlier manual 502 response. Infrastructure authorization failures remain HTTP 503 and do not retire a healthy bridge. The earlier scalar-review archive records the contract at that earlier head; this integration supersedes its 503 policy-denial wording.

Saved thresholds are updated atomically: omitted values retain current database values, explicit null clears a field, and enabling requires at least one saved or supplied threshold. Published override-only policies and 422 validation remain supported. An empty successful poll supersedes old standard measurements with unavailable placeholders; enabled policies invalidate selection immediately, while disabled policies retain their existing routing semantics.

For example, an enabled weekly-only override that changes while a bridge turn waits for dispatch must reject the unsent turn with `account_usage_limit_reached`, while overlapping dispatched work remains with its original owner and settles normally. A failed authorization read instead returns `account_usage_limit_authorization_failed` and leaves a healthy transport available for retry.

## Architecture and history

One typed fresh authorization snapshot replaces the obsolete cached owner-policy reader. Canonical routing-pool evidence stays separate from eligible capacity, preserving fallback and error precedence without counting blocked accounts. Local injected clocks, scheduler ownership, and the final sticky generation fence remain in place. Equivalent tests are consolidated only where the published suite covers the same product path.

The original scalar revision parent remains valid. A merge revision joins the published override head to the existing local/upstream merge. Upgrade tests build actual schemas from both parent declarations, preserve enabled and disabled saved thresholds, and verify one canonical head without schema drift.

## Verification

Combined bridge/WebSocket/retry/cancellation coverage passed 1,596 tests. Contract tests passed 176 cases and the final admission-boundary slice passed 12. The broader core suite passed 1,223 tests with 27 skips; its only failure was an older assertion expecting the throttled header refresh to finish when immediate selection invalidation completed. The corrected test passed, and the complete direct Responses/live-ingest/topology rerun passed 143 tests with four PostgreSQL-specific skips. The additional warmup/routing/dashboard slice passed 314 tests with eight PostgreSQL skips; its old SSE error-type expectation was corrected and verified in the complete Responses rerun.

Evaluator/typed authorization coverage passed 87 tests. Historical upgrade coverage passed three local/upstream starting revisions and a database built from the published graph, retaining saved defaults and overrides with no schema drift. `make migration-check` reports one head, policy OK, and no schema drift. Repository lint, architecture/cancellation/timing/settings checks, backend typing, frontend lint/types/production build, 222 focused account UI tests, and 371 dashboard/mock tests passed. Strict validation passed both changes and all 67 main specs.

PostgreSQL is not configured in this checkout; current SQLite checks do not substitute for PostgreSQL CI. The previous published audit's PostgreSQL evidence remains historical. No claim is made that current-head cloud CI has completed.
