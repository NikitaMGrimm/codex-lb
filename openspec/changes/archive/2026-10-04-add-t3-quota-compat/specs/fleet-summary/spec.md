## ADDED Requirements

### Requirement: T3 quota compatibility is read-only

The system SHALL expose `GET /v0/management/auth-files` and `POST /v0/management/api-call` for T3 quota display. Both routes SHALL require a valid Bearer API key and honor fleet account scoping and quota visibility. The account list SHALL contain only Codex accounts visible to that key. The API call route SHALL return stored primary and secondary quota windows only for the listed account and the Codex usage URL. It SHALL return an empty reset-credit list for the Codex reset-credit URL. It SHALL reject all other URLs, methods, and account identifiers without making an upstream request.

#### Scenario: T3 reads a visible account

- **WHEN** a permitted key lists accounts and requests the Codex usage URL for one listed account
- **THEN** the response contains that account's persisted quota percentages and reset times
- **AND** no account credential is returned

#### Scenario: T3 requests an unsupported operation

- **WHEN** a client requests another URL or a write method
- **THEN** the system rejects the request without forwarding it
