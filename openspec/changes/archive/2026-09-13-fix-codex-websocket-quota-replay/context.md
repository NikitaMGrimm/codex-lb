# VPS integration and implementation

This branch preserves the deployed migration parent for the existing scalar usage-limit revision. A new merge revision joins its deployed lineage, the current upstream head, and PR #1528 window overrides without rewriting applied history.

Quota failover is limited to requests rejected before acceptance/output, with complete supplied or verified retained input. It preserves all portable messages and tool call/results, removes response-owned IDs/encrypted reasoning through the existing projection, and adds a continuity notice. It never falls back to the newest user message alone. Files and hard-affinity owners remain protected. The upstream PR branch is not modified.

Verification: the merged graph has 266 revisions and one head. A synthetic SQLite upgrade from the deployed head preserves an 80% account cap and adds null window overrides; migration policy and schema drift checks are clean. The topology authoring check against the old deployed commit rejects the already divergent upstream branches. Graph validation therefore uses `--base-ref=` for this deliberate integration, without rewriting applied migration ancestry.

Focused verification covers the WebSocket quota-switch path, ownership/output refusal, and the preserved HTTP bridge best-effort recovery path. Broad suites and live rollout are intentionally omitted at the owner's request.
