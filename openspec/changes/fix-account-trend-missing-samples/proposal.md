# Fix missing account trend samples

## Why
The dashboard merges quota series using only one series' timestamps and substitutes zero for absent samples. This can discard real observations and display exhaustion without an observation. The legend also advertises absent windows.

## What Changes
- Preserve the union of observation timestamps and represent absent samples as gaps.
- Show legends for available series and use Monthly for monthly account tooltips.

## Impact
Frontend quota charts only. No API, persistence, or routing changes.
