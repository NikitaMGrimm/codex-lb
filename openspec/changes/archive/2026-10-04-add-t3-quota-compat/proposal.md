## Why

T3 Code reads pooled subscription quotas through two CLIProxyAPI management paths. Codex LB already has a scoped, API-key-authenticated fleet summary, but T3 cannot consume that format directly.

## What Changes

Expose a read-only compatibility projection for T3. It must use the existing fleet visibility policy, never forward arbitrary API calls, and report no redeemable reset credits. This keeps the Codex LB pool and credentials authoritative.
