## 1. Implementation

- [x] 1.1 Replace the frontend Bun lockfile and commands with npm equivalents.
- [x] 1.2 Move Docker and Compose frontend stages to pinned Node.js/npm.
- [x] 1.3 Move CI, release, Dependabot, and environment setup to npm.
- [x] 1.4 Update active developer documentation, hints, and coupled tests.

## 2. Validation

- [x] 2.1 Run `npm ci`, lint, typecheck, tests, and production build.
- [x] 2.2 Run directly coupled backend tests and strict OpenSpec validation.
- [x] 2.3 Verify the frontend build inside the pinned Node container and confirm
      its manifest publishes native Linux AMD64 and ARM64 images.
