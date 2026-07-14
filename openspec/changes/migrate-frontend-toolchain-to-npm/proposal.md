## Why

The frontend build currently depends on Bun even though the supported WSL and
VPS environments already provide the standard Node.js/npm toolchain. The Bun
container stage also introduced an avoidable architecture-specific deployment
failure on ARM64.

## What Changes

- Replace Bun with pinned Node.js 22.23.1 and npm 10.9.8 for local development,
  CI, release packaging, Compose, and production image builds.
- Replace `bun.lock` with npm's deterministic `package-lock.json` and use
  `npm ci` for clean installs.
- Keep Node.js confined to frontend development and build stages; the Python
  runtime images remain unchanged.

## Capabilities

### Modified Capabilities

- `frontend-architecture`: define the supported, reproducible frontend build
  toolchain and lockfile contract.

## Impact

Frontend dependency installation, developer commands, Docker build inputs,
GitHub Actions caches, release packaging, and dependency automation now use npm.
