## ADDED Requirements

### Requirement: Best-effort owner-loss recovery preserves portable task context and tools

When an HTTP bridge continuity owner is unavailable before visible output, the
proxy MUST prefer an account-neutral full resend over a newest-message replay.
Projection MAY remove the known Codex Desktop metadata fields `create_time` and
`content_item_kinds` while retaining a nonblank `turn_id`. Unknown internal
metadata MUST remain fail-closed. Projection MAY remove blank `input_text` or
`text` fragments from a completed direct-tool output list, but MUST preserve all
substantive output and the matching call/output relationship.

If full history remains unportable and recovery uses only the newest portable
user text, the fresh request MUST preserve explicitly supplied account-neutral
top-level tool controls. When a projected Responses-Lite input begins with an
account-neutral `additional_tools` bundle and a valid adjacent developer
instruction, recovery MUST retain that portable prefix. Account-scoped files,
images, response IDs, encrypted reasoning, and unknown metadata MUST NOT move
to the replacement account.

After a fresh recovery response completes on a replacement account, the proxy
MUST attempt to rebind the original locally owned durable logical task to that
account. The write MUST compare the captured owner epoch and both captured
continuity anchors, MUST clear obsolete anchors on success, and MUST leave a
concurrently advanced row unchanged.

#### Scenario: Current Desktop history remains replayable

- **GIVEN** a self-contained full history carries `turn_id`, `create_time`, and
  `content_item_kinds` metadata
- **AND** completed tool outputs contain substantive text plus blank text parts
- **WHEN** the owner account becomes unavailable before output
- **THEN** projection retains the substantive history and direct-tool pairs
- **AND** the account-neutral full resend is preferred over newest-message
  recovery

#### Scenario: Latest-message recovery retains Responses-Lite tools

- **GIVEN** account-scoped history prevents a full resend
- **AND** the input begins with an account-neutral `additional_tools` bundle
  and valid adjacent developer instruction
- **WHEN** recovery retains only the newest portable user message
- **THEN** the fresh request also retains that tool bundle and developer policy
- **AND** it omits the account-scoped history

#### Scenario: Successful replacement owns later task continuity

- **GIVEN** the original durable task row is locally owned and bound to account A
- **AND** a server-namespaced recovery lane completes on account B
- **WHEN** the proxy persists the replacement
- **THEN** it compare-and-sets the original row to account B and clears the old
  anchors
- **AND** a concurrently changed epoch or anchor fences the write
