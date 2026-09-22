# Verification

This local change is separate from the account usage-limit feature. It corrects missing chart samples, monthly chart labels, and quota smoothing state carried across account selection.

Built-in browser verification used real components with synthetic quota observations. Switching from dual-window to weekly-only and monthly-only accounts reproduced stale quota bars; resetting state by account ID removes them. Sparse-series regression coverage confirms missing observations remain gaps rather than zero.

The exact cause of the original live monthly-history screenshot was not established without its source data. No production access was used.

Validation after isolating this change onto upstream `3d23d53f89dbbaa2353040a30451cf90ca48ee92`: 153 account frontend tests passed; TypeScript, changed-file ESLint, production build, and strict change validation passed. The built-in browser reproduced the stale Plus-to-Free display on unmodified upstream components and verified the corrected Monthly display. Synthetic before/after captures are in `evidence/`.

## Sparse-series visual reproduction

The actual baseline and fixed chart components receive identical synthetic inputs at midnight UTC in September 2026. Primary samples: days 14–20 with remaining percentages 80, 77, 74, 71, 68, 65, 62. Secondary samples: days 14–19, 21, 22 with remaining percentages 95, 94, 93, 92, 91, 90, 86, 85. There is no secondary observation on day 20.

`evidence/sparse-before.png` shows upstream rendering a false zero on day 20 and discarding days 21–22. `evidence/sparse-after.png` shows the gap and retains the final 86-to-85 percent segment. Both are built-in browser screenshots of local synthetic data, cropped to the chart and captions.
