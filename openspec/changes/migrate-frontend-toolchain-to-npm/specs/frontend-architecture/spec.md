## ADDED Requirements

### Requirement: Frontend builds use a reproducible Node.js and npm toolchain

The project MUST use Node.js 22.23.1 and npm 10.9.8 with
`frontend/package-lock.json` as the frontend dependency lock contract. Clean
local, CI, release, Compose, and container-build installs MUST use `npm ci`.
Node.js MUST remain a build-time dependency and MUST NOT be added to the Python
application runtime image.

#### Scenario: A clean frontend build uses the committed npm lockfile

- **WHEN** a developer, CI job, release job, or container build installs frontend dependencies
- **THEN** it uses npm with `frontend/package-lock.json`
- **AND** it rejects dependency resolution that differs from the committed lockfile

#### Scenario: Production runtime does not include the frontend toolchain

- **WHEN** the production application image is assembled
- **THEN** frontend assets are copied from the Node.js build stage
- **AND** the runtime stage does not inherit Node.js or npm
