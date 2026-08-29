## Context

The existing owner-loss path deliberately constructs a new account-neutral
request rather than copying an envelope that may contain account-owned state.
That remains the right boundary, but the projector and fresh-request builder do
not match current Codex Desktop's portable wire shape. The server-namespaced
recovery lane also protects the one replacement dispatch without changing the
broad task binding that later turns consult.

## Goals / Non-Goals

**Goals:**

- Preserve the maximum self-contained conversation history present in the
  request when an owner account becomes unavailable.
- Preserve the tool surface and its developer policy whenever their verified
  declarations are present.
- Keep later turns on the successfully selected replacement account.
- Make stage selection and rejection causes visible without logging payloads.

**Non-Goals:**

- Moving account-scoped files, images, encrypted reasoning, response IDs, or
  unknown metadata between accounts.
- Fetching missing history from the Codex Desktop database inside codex-lb.
- Adding a setting, fallback daemon, schema migration, or dashboard control.

## Decisions

- Treat only `turn_id`, `create_time`, and `content_item_kinds` as known
  portable internal metadata. Projection retains `turn_id` and removes the two
  presentation/bookkeeping fields. Unknown fields remain visible so the
  existing classifier still fails closed.
- Remove blank `input_text` or `text` parts only from completed direct-tool
  output lists. Preserve every substantive part; represent an entirely blank
  output as the existing accepted empty-string result.
- Rebuild the fallback envelope from safe fields, copying explicitly supplied
  top-level tool controls. For Responses-Lite, prefer the verified
  `additional_tools` plus adjacent developer message, then the bundle alone.
  The canonical account-neutral classifier still validates the final body.
- Keep the server-namespaced replay lane. Once that lane completes, compare and
  set the original durable row using its owner instance, owner epoch, and both
  captured anchors; on success, bind it to the replacement account and clear
  obsolete anchors. A concurrent owner or continuity advance fences the write.
- Durable-rebind failure after a completed upstream response is observable but
  does not retract already emitted output.

## Risks / Trade-offs

- [Risk] Metadata normalization could accidentally hide a future account-owned
  field. -> Mitigation: normalize an exact three-field allowlist; all unknown
  fields remain fail-closed.
- [Risk] Clearing an anchor could race a newer turn. -> Mitigation: compare both
  captured anchors under the original owner epoch.
- [Risk] Latest-message recovery still lacks history absent from the request.
  -> Mitigation: preserve tools and the task deeplink, while preferring the
  sanitized full-history stage whenever it validates.
