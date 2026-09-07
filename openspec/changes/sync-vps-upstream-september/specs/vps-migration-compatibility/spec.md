## ADDED Requirements

### Requirement: Preserve deployed migration ancestry
The VPS fork MUST preserve the contents and ancestry of all previously deployed custom migrations and MUST provide a single-head upgrade path to current upstream.

#### Scenario: Upgrade the deployed database
- **WHEN** the database is at the deployed 20260828 custom merge revision
- **THEN** upgrade SHALL reach the sole current head without losing account usage-limit settings

### Requirement: Respect denied-anchor fences during continuity fallback
The VPS best-effort replay path MUST NOT retry a proxy-injected anchor rejected by the current denied-anchor fence.

#### Scenario: A sibling rejects an anchor before dispatch
- **WHEN** the captured denied-anchor fence advances before the request dispatches
- **THEN** the request SHALL fail closed without opening a replacement account session
