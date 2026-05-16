# Local vs Online Gap Report

Date: 2026-05-15

## Baseline

- Public GitHub `main`: `064b21ee08ab0ea16a5723c8fc0ce18174001fbe`
- Local cleanup branch: `codex/foundation-cleanup`
- The public repository is the vision scaffold. The local branch is the implementation branch.

## Public Repository Reality

The public tree advertises a broad architecture, but the actual active service tree on `main` only contains:

- `services/agents`
- `services/api-gateway`
- `services/memory`

It also has only one shared package, `packages/config`, and test folders limited to `tests/integration` and `tests/simulation`.

## Local Branch Additions

The local branch now adds the concrete foundation that the public README only described:

- runnable FastAPI gateway
- one-command local host runtime with persistent SQLite
- PostgreSQL-backed local persistence
- canonical market normalization
- local Ollama integration boundary
- research crawling with paginated documents
- bounded browser research automation with source-page trails
- optional browser-automation adapters
- visual-learning starter contracts
- clearer service ownership
- canonical `infrastructure/`, `tools/`, `packages/`, `research/`, and `tests/` homes

## Still Missing

The local branch is materially ahead of public `main`, but it is still not the final system envisioned online. The following remain incomplete:

- durable auth, RBAC, MFA, and session lifecycle
- migrations and production-grade data models
- live market providers, replay, and provenance
- portfolio accounting and valuation
- event bus, workers, and WebSocket fan-out
- bounded AI agents and AI broker controls
- live broker execution with approvals and kill switches
- mobile and device clients beyond scaffolding
- Web3 read-only aggregation, then guarded signing
- quantum work beyond experiments
- enterprise deployment after public hardening

## Architecture Decision

The repository should follow a practical monorepo layout:

```text
apps/
services/
packages/
infrastructure/
tools/
tests/
research/
docs/
archive/
```

Deployable software lives in `apps/` or `services/`. Shared libraries live in `packages/`. Experiments that are not ready to operate in production live in `research/`. Historical material stays in `archive/`.
