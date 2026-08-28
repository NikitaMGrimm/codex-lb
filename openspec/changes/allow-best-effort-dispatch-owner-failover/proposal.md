# Allow best-effort dispatch-owner failover

## Summary

Let an unpinned client-supplied Responses history move to another account when
the selected account fails before any output becomes visible.

## What Changes

- Release ownership created only by the failed dispatch before selecting the
  next account.
- Reuse verified HTTP-bridge full-history replay when a durable owner reaches
  its configured account usage limit.
- As a final best-effort resume, discard an unavailable owner's stale response
  anchor when the remaining current input is independently account-neutral,
  including after its bridge disconnects without producing a response event.
- Keep previous-response, turn-state, uploaded-file, and single-account
  ownership fail-closed.
- Reuse the original client payload without adding configuration or storage.

## Impact

This personal-fork behavior favors task continuity over strict replay proof for
one pre-visible failure case. It adds no setting, schema, UI, or operator step.
