# Account usage limits

## Purpose and model

Operators can reserve quota for direct use by limiting how much Codex LB consumes from an account. This combines the scalar policy from PR #1528 with the independent windows and reserve presentation proposed in PR #2147.

One enabled flag controls a default maximum-used percentage and optional 5-hour and weekly overrides. An absent override inherits the default; without a default, unmatched windows remain unrestricted. Disabling retains saved values, while removal clears them. Existing scalar policies retain their behavior without a conversion to the lowest window threshold.

With 54% consumed and an 80% cap, the provider has 46 percentage points remaining: 20 reserved and 26 usable. With primary/weekly usage of 65%/75% and caps of 70%/90%, both windows remain available; primary usage of 72% blocks the account. The editor displays reserve percentages, while the API stores maximum-used percentages.

## Observation and ownership boundaries

The shared evaluator normalizes weekly-only and monthly-only observations. Window overrides match duration, so monthly and other nonstandard windows use the default. Applicable missing, stale, or elapsed observations fail closed until a fresh measurement arrives. A reset deadline alone does not prove a new zero measurement. Unknown placeholders remain current-state evidence but are excluded from numeric history and demand calculations.

The policy is a hard eligibility gate, including for additional-quota requests. It does not change persisted upstream status. Continuity owners stay pinned: bridge/WebSocket dispatch and every warmup surface authorize the selected account from committed database state. A policy change after an authorization read is not retroactive; already dispatched requests retain ownership and settlement paths. The design document records cache, timeout, retry, and cleanup boundaries.

## Migration topology

The scalar migration follows `20260918_000000_merge_scim_and_overflow_heads`; the override migration follows the scalar migration. Existing accounts start disabled. Override downgrade disables policies with no scalar threshold before removing the override columns. SQLite and PostgreSQL upgrade/downgrade coverage checks the resulting constraints and data.

## Published PR audit

The audit starts at GitHub PR #1528 head `242a0f937`, against base `ec994599`: 12,390 additions, 785 deletions, 135 files. Work stays local on `fix/pr1528-usage-audit` in a separate worktree, preserving the earlier scalar-only checkout. Verification uses this head's frozen dependency locks.

The audit fixes stale toggles overwriting newer thresholds, unhandled mutation rejection, lease cleanup after WebSocket expiry, and reserve controls offered for incorrect durations. It consolidates telemetry writes, warmup rejection handling, and retry tests. Duplicate assertions remain covered at the public paths. PostgreSQL reconciliation tests wait for the identity read to finish before releasing the writer; transient-stream tests fail whichever account is selected first, avoiding random selection assumptions.

A local component preview compares the published and reviewed controls for 60-minute and 1440-minute windows. It uses synthetic accounts and makes no provider requests. The feature change remains active while the PR is being reviewed locally.

## Audit verification and size

Local checks used the published head's frozen dependencies. The affected unit suite passed 3,801 tests with three obsolete locking scenarios skipped; the final duplicate removal passed its focused 310-test suite. The wider frontend slice passed 556 tests, followed by 21 focused tests after removing its duplicate case. WebSocket, cancellation, and demultiplexing checks passed 229 tests. The bridge/telemetry/proxy/warmup integration slice passed 430 tests with 15 backend-specific skips; its one flaky retry test was corrected, then all 57 retry tests passed. PostgreSQL checks passed eight migration tests, 59 authorization/telemetry tests (five SQLite-specific skips), and nine selected policy/SQL-interruption tests. The corrected PostgreSQL reconciliation test passed three additional runs.

Repository lint, architecture ratchets, type checks, frontend lint/type checks/build, strict change validation, and all 66 main-spec validations passed. Migration topology also passed against the actual PR base, with exactly two added revisions. GitHub's head and base still match the recorded baseline. These are local checks; the review commits have not been published to run cloud checks.

Both size columns below compare the entire PR against `ec994599`; tests include frontend mock support. Added/deleted are raw Git diff counts, while net is added minus deleted.

| Entire PR | Published `242a0f937` | Reviewed |
| --- | ---: | ---: |
| Added | 12,390 | 12,194 |
| Deleted | 785 | 836 |
| Net growth | 11,605 | 11,358 |
| Changed files | 135 | 135 |

Net growth by category: production: +2,672 to +2,648; tests: +8,006 to +7,802; docs: +925 to +906; other: +2 to +2.
