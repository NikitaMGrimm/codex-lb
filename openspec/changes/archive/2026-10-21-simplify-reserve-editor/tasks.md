## 1. Editor

- [x] 1.1 Rewrite `AccountUsageLimitControl` as per-window reserve rows with remaining and usable readouts, live reached marking, and narrow suffixed inputs without spinners.
- [x] 1.2 Map rows to `percent` / `percent5H` / `percentWeekly`, preserving hidden overrides, untouched defaults, and saved precision; clearing every row removes the policy.
- [x] 1.3 Always-visible switch, blocking-state badge only, Save/Cancel on change, Escape to discard.
- [x] 1.4 Update English, Korean, and Simplified Chinese strings; drop unused keys.

## 2. Verification

- [x] 2.1 Unit tests for row derivation, previews, save mapping, removal, precision, toggling, and blocking labels; integration flow updated.
- [x] 2.2 `bun run lint`, `bun run typecheck`, `bun run test`, `openspec validate simplify-reserve-editor --strict`.
- [x] 2.3 Before/after screenshots and a matched edit/save/toggle recording with the local Playwright harness.
