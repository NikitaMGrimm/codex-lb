## Context

See [proposal.md](proposal.md). The branch already shares a pure policy evaluator and uses selection-cache generations to detect stale admission. Bridge readers need the pending lock to settle other turns; send serialization uses a separate lifecycle lock.

## Goals / Non-Goals

Close demonstrated authorization gaps using the current evaluator and cleanup paths. Preserve the scalar policy, upstream health semantics, existing ownership, and disabled-feature behavior. This review does not rebase or publish the divergent branch.

## Decisions

- Put the final bridge authorization after lifecycle-lock waits and durable preparation, before pending publication and send. Keep early admission checks to avoid queueing known-denied work. Merely adding another pre-lock check does not close the race.
- If selection data changes during sticky persistence, release the lease and return the existing retryable `selection_state_changed` error. Avoid speculative compensating affinity writes that can overwrite another request's ownership.
- Represent an empty successful poll using existing no-data placeholders in all standard slots for enabled policies. This supersedes historical weekly and monthly shapes without adding columns. Partial valid shapes continue using the existing normalization rules.
- Retain the shared evaluator and existing cache rather than introduce policy-specific services or more settings. Simplify redundant typed access and work only where verified behavior stays identical.

## Risks / Trade-offs

- A slow authorization read holds send serialization longer; it remains deadline-bounded and does not hold the reader's pending lock.
- An empty successful poll now blocks an enabled policy immediately. Fresh valid telemetry or disabling the policy restores eligibility.
- Affinity may already be committed when a late policy invalidation is noticed. Returning a retryable error preserves that ownership and avoids unsafe rollback.
- Upstream reporting and already-dispatched requests can still overshoot a cap; the guarantee remains observation-bound.
