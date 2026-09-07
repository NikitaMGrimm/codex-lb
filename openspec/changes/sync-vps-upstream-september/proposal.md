# Sync VPS fork with current upstream

## Why
The deployed fork predates upstream recovery and scheduler fixes. Preserve its required continuity behavior while replacing superseded patches.

## What Changes
- Adopt upstream v1.25.0-beta.2 and the current per-account usage-limit implementation.
- Keep account-neutral best-effort continuity and expired-cooldown transitions.
- Use upstream bounded cleanup, poisoned-anchor recovery, and edge-challenge handling.
- Preserve every deployed migration and add a no-op graph join.

## Impact
Proxy retry behavior and database upgrade compatibility; no production deployment in this change.
