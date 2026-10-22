## Why
Refresh the VPS fork with current upstream and authored PRs while retaining VPS recovery, attribution, and applied migration history.

## What Changes
- Integrate upstream main, current per-account usage limits, and dependency security fixes.
- Keep every deployed migration unchanged and join the added PR lineage with a no-op successor.

## Impact
Codex LB only. Account data and saved limits remain intact. Image rollback uses the existing paired state watchdog.
