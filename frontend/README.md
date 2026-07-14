# Frontend (Node.js + npm + Vite + React + TypeScript + SWC)

This frontend is built with Node.js, npm, Vite, React, TypeScript, and SWC.

## Prerequisites

- Node.js 22.23.1
- npm 10.9.8

## Setup

```bash
cd frontend
npm ci
```

## Development

```bash
npm run dev
```

Vite dev server runs on port `5173` by default and proxies API routes to FastAPI:

- `/api/*`
- `/v1/*`
- `/backend-api/*`
- `/health`

## Build

```bash
npm run build
```

Production assets are emitted to `../app/static`.

## Quality

```bash
npm run lint
npm run typecheck
npm run test
npm run test:coverage
```
