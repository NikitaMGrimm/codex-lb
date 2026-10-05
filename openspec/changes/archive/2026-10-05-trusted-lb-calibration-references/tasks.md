## 1. Implementation

- [x] 1.1 Add persisted trusted references and settings UI; verify API roundtrip, preservation, and component tests.
- [x] 1.2 Use fresh current-cycle trusted-peer calibration excluding the target; verify attribution regressions, first readings, missing references, and Pro ratio changes.
- [x] 1.3 Verify additive migration upgrade/downgrade and recovery compatibility without changing published revisions.

## 2. Delivery

- [x] 2.1 Run affected native checks, frontend checks, and strict OpenSpec validation; sync and archive verified requirements.
- [x] 2.2 Publish the reviewed fork source, run required VPS checks, and submit narrow Codex LB deployment with recorded rollback compatibility.
- [x] 2.3 Select the owner's two clean references through the application settings repository with version checks, preserve the Pro ratio, and verify live estimates and container impact.


## Verified delivery evidence

Published runtime source `95fbf1d5fbe072bde1efcaeb0b3207312307b05c` deployed
through VPS operation `20261005T183232Z-ffbc1dd3006345bc`, exit code 0.
164 focused backend checks, 49 focused frontend checks, all 1,720 frontend
tests, native lint/type/build/topology checks, three new migration cases,
six recovery cases, SQLite/PostgreSQL schema checks, and strict delta/all69
specifications passed. Required full VPS checks passed on the final pin.
Live readiness, source image label, single migration head, and target
provenance verified. Exactly two clean Team references selected with version
checks; ratio 20 and all unrelated settings preserved. Clean Team readings
98.94% and 101.08%, Plus 76.42%, Pro 34.89%. No unrelated container changed.
Main specs were already synced before deployment; archival skips re-sync to
preserve the existing trusted-selection requirement without duplication.
