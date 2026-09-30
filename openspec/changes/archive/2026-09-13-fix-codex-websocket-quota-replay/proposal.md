# Fix Codex WebSocket quota replay compatibility

## Why

The deployed direct WebSocket path binds a request to the selected account when its replay-safety classifier does not recognize the request shape. Known Codex client metadata and `reasoning.context=all_turns` cause this rejection. The Responses-Lite normalization path itself adds that reasoning field. A pre-created quota error then produces one same-account replay, followed by a terminal usage-limit error. T3 treats that backend terminal as failed.

The desktop app and T3 do not have identical overall execution paths, but isolated tests show that both Codex backend binaries stop when a raw quota terminal reaches them. A binary update alone is not an established fix. The precise cause of the observed difference in overall failure frequency remains unverified; this proposal addresses the reproduced LB defect.

## What changes

1. Recognize the verified account-independent Codex metadata fields and `reasoning.context` value in replay validation. Validate values explicitly; retain rejection of unknown shapes.
2. On quota rejection before acceptance/output, exclude the rejected account when the retained request can safely move. Do not spend the retry budget on the known exhausted account.
3. For full-history Responses-Lite requests, reuse existing transcript projection only with sufficient history/ownership evidence. Preserve instructions, portable tools, user messages, completed tool calls and their results. Do not silently fall back to only the latest user message.
4. Keep actual uploaded-file ownership, stored-response-only continuations, hosted-tool state, and already-exposed output protected.
5. Record bounded reason codes for replay refusal (no prompts, tool arguments, credentials, or raw metadata values).

## Status

Implemented on the VPS branch after merging PR #1528 at 9324db0fe898104bb1e8d2aff186b3b33ddc4903. Mocked end-to-end WebSocket quota transitions pass for plain, metadata, reasoning-context, inline namespace, and projected full-history requests; unknown metadata remains refused. The captured T3 request passes the same replay preparation, preserving the supplied portable history. Focused ownership/output and existing HTTP bridge recovery regressions pass. A live T3 transition remains an operator follow-up after deployment.

## Scope

Direct WebSocket quota failover plus the owner-requested upstream PR integration. The replay fix itself needs no schema changes; the integration adds a merge revision preserving the already deployed migration ancestry. Deployment is deliberately left to the owner because this session depends on the running LB.
