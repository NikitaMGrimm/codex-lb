## Context

See proposal.md. Current-cycle accounting and deadline safeguards already exist. Historical replay found that explicit clean peers agree far better than calibration from unknown users.

## Goals / Non-Goals

**Goals:** trusted reference selection, fresh current-cycle calibration, target exclusion, and preserved Pro ratio semantics.

**Non-Goals:** request-level causal attribution or a new statistical model.

## Decisions

Store selected account IDs as JSON in one settings column, defaulting to an empty list. Settings UI selects accounts without hardcoded emails or IDs. Empty selection disables positive-cost estimates instead of silently trusting every account. Peer conversion uses each selected peer's current used percentage and successful costs over its current cycle; a reference target uses only other selected peers.

## Risks / Trade-offs

- A reference later gains external users → owner can remove it in Settings.
- Small or changing workloads → estimates remain approximate and uncapped; no minimum usage threshold is added.
- Additive column changes migration head → verify fresh upgrade, downgrade, and recovery compatibility; preserve published migrations.

## Migration Plan

Deploy the additive migration and binary, then select the owner's two clean Team accounts through the authorized operator session using the application settings repository, optimistic version checks, and cache invalidation. Manual rollback requires downgrading to the previous migration head using the new build before reversing the source pin; this drops only the reference selection and preserves existing settings and usage. The managed cutover watchdog retains its paired pre-cutover rollback snapshot. Preserve the owner's independently edited Pro ratio when saving references.
