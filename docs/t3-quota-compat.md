# T3 Code quota display

T3 Code's CLIProxyAPI hub form can display Codex LB account quotas through a restricted compatibility surface. Create an API key in Codex LB with the `upstream_limits` and `account_pool_usage` usage sections. Scope the key to the accounts you want to display. In T3 Code's provider settings, add a hub with the private Codex LB origin as **Hub URL**, that API key as **Management key**, and a descriptive label.

Codex LB answers only account listing and stored Codex usage reads on this surface. It reports no reset credits. It does not forward the form's requested URLs to upstream services or expose account OAuth credentials. The global setting that hides upstream quota from API keys also hides this display. The API key remains a Codex LB API key, so protect it like the existing proxy keys.

The compatibility paths are `/v0/management/auth-files` and `/v0/management/api-call`. T3 appends them to the hub origin itself; do not enter `/backend-api/codex` in the URL field.

*Spec: [fleet-summary](https://github.com/Soju06/codex-lb/tree/main/openspec/specs/fleet-summary)*
