## Why

Real Codex Desktop full-history resends include portable bookkeeping fields such
as `create_time` and `content_item_kinds`, and completed custom-tool outputs may
contain empty text fragments. The cross-account replay classifier currently
rejects those otherwise self-contained histories. Its newest-message fallback
then drops the Responses-Lite tool declaration prefix, and the successful
replacement lane does not update the original task's durable account binding.
The result is a context-poor, tool-less task that can repeat the same fallback
on every follow-up.

## What Changes

- Normalize only the known portable Codex Desktop metadata fields and empty
  text fragments while projecting a fresh account-neutral replay.
- Preserve account-neutral top-level tools and the Responses-Lite
  `additional_tools` plus adjacent developer-instruction prefix when recovery
  must fall back to the newest portable user message.
- After a replacement response completes, use the original durable owner epoch
  and continuity anchors to rebind that logical task to the replacement account
  and clear its obsolete account-owned anchors.
- Log each rejected recovery stage separately from the ultimately selected
  replay stage and durable-rebind outcome.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `responses-api-compat`: Owner-loss recovery accepts portable Desktop history,
  preserves available tools, and keeps later task continuity on the replacement
  account.
- `proxy-runtime-observability`: Recovery diagnostics identify rejected and
  selected replay stages plus durable-rebind outcomes.

## Impact

- `app/modules/proxy/replay_safety.py`
- `app/modules/proxy/_service/http_bridge/streaming.py`
- Focused replay-safety and HTTP bridge regression tests.
- No schema, setting, dependency, dashboard, or public API change.
