# Simplify the reserve editor

## Why

The reserve editor shows a shared reserve and up to two window reserves side by side, with blank windows inheriting the shared value. On a typical 5-hour + weekly account the shared value then has no effect once both windows are set, yet it stays on screen as if it did. The effect of a value is visible only in the usage bars after saving, so a reserve above the remaining quota silently blocks routing. The card also mixes three ways to stop reserving (switch, Remove, clearing values), shows a runtime `Active` badge that reads as the switch label, and changes layout between the unconfigured and configured states.

## What Changes

- Show one row per reported window with the reserve that applies to it, its provider remaining, and what Codex LB could use with the unsaved value. Mark a window the draft would block as reached before saving.
- Map rows to the existing default and override fields without exposing inheritance: a window equal to the default keeps inheriting it, and the default is only edited when some reported window depends on it alone.
- Keep the switch visible in every state; it is unavailable until a policy exists. Clearing every row and saving removes the policy, replacing the separate Remove button.
- Show `Limit reached` / `Usage unavailable` (the account list labels) only for blocking states; drop the `Active` badge.
- Show Save and Cancel only with unsaved changes; Escape discards them.
- Rename the reserve toasts to match the editor's vocabulary.

No API, schema, routing, or settings change.
