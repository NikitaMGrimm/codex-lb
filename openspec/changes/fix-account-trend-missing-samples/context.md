# Verification

This local change is separate from the account usage-limit feature. It corrects missing chart samples, monthly chart labels, and quota smoothing state carried across account selection.

Built-in browser verification used real components with synthetic quota observations. Switching from dual-window to weekly-only and monthly-only accounts reproduced stale quota bars; resetting state by account ID removes them. Sparse-series regression coverage confirms missing observations remain gaps rather than zero.

The exact cause of the original live monthly-history screenshot was not established without its source data. No production access was used.

Validation after isolating this change onto upstream `3d23d53f89dbbaa2353040a30451cf90ca48ee92`: 153 account frontend tests passed; TypeScript, changed-file ESLint, production build, and strict change validation passed. The built-in browser reproduced the stale Plus-to-Free display on unmodified upstream components and verified the corrected Monthly display. Synthetic before/after captures are in `evidence/`.
