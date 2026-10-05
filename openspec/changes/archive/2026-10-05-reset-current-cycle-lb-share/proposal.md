# Current-cycle LB quota attribution

## Why

The indicator currently combines several quota cycles and suppresses estimates above 100%, making it misleading beside a fresh weekly quota. Reset accounting also loses the first nonzero observation and misses resets whose usage does not decrease.

## What Changes

Change attribution to the current weekly/monthly cycle, use fresh reset deadlines to recognize renewals, include the first observed quota usage, and show uncapped estimates. Keep recent peer calibration independent of the target cycle so new cycles can receive estimates without waiting for a previous 100%-used reading or a large peer sample. No routing, capacity settings, storage schema, or runtime dependencies change.
