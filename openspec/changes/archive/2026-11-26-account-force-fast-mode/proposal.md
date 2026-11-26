# Force Fast mode per account

## Why

Operators need to choose which subscription accounts always use Fast mode while keeping a shared client and pool.

## What Changes

- Add a persistent Force Fast mode switch to each account's dashboard actions.
- Apply the priority tier to supported inference requests at dispatch for accounts with the switch enabled.
- Recompute the override on retries and honor the global Prohibit Fast Mode setting.

## Impact

- Affected specs: fast-mode-policy
- Affected code: dashboard Accounts, account persistence, subscription inference dispatch
