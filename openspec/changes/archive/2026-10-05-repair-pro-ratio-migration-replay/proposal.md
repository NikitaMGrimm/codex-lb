# Repair Pro ratio migration replay

## Why

The deployed fork's Pro attribution column migration cannot replay when database
recovery rewinds or loses its ledger. Four existing recovery regressions fail
with duplicate-column errors even though the physical column already exists.

## What Changes

The locked application migration runner will recognize the already-applied,
compatible Pro ratio column at its exact migration step, preserve its data, and
let Alembic advance that step without repeating the DDL. Incompatible columns
fail with explicit guidance. Published revisions, graph, and schema stay intact.

A focused quota review also closes regressed-deadline replay after a metadata
gap, retains the confirmed deadline for API/UI expiry, and shows zero immediately
when logged LB cost is zero even without peer calibration.

## Impact

Database recovery and startup/CLI upgrade execution only. Fresh upgrades still
run the published migration; other pending steps still execute normally.
