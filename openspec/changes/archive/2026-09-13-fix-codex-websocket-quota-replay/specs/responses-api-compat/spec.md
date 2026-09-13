## ADDED Requirements

### Requirement: Portable Codex WebSocket quota recovery
The proxy SHALL distinguish account-independent Codex request metadata from references to stored account-owned state. On a quota rejection before response acceptance or downstream output, a request proven self-contained SHALL be retried on an eligible different account with the rejected account excluded from that retry series.

#### Scenario: Known Codex metadata does not create account ownership
- **GIVEN** a self-contained request includes supported session/thread/turn diagnostic metadata and `reasoning.context=all_turns`
- **WHEN** the selected account rejects it for quota before acceptance
- **THEN** the proxy retries a different eligible account without emitting the intermediate quota terminal
- **AND** the portable conversation and tool definitions remain available

#### Scenario: Missing stored state prevents cross-account replay
- **GIVEN** a continuation depends on an account-owned upload, hosted-tool state, or prior response that cannot be reconstructed
- **WHEN** that owner rejects the request for quota
- **THEN** the proxy does not send an incomplete or owner-dependent request to a different account

#### Scenario: Output and side effects are not replayed blindly
- **GIVEN** response output or a tool invocation has already been exposed
- **WHEN** a later quota error arrives
- **THEN** the pre-acceptance replay path is not used

#### Scenario: Replay refusal is diagnosable without content disclosure
- **WHEN** a replay-safety check refuses account switching
- **THEN** diagnostics identify a bounded reason code without logging prompts, tool arguments, credential values, or conversation text
