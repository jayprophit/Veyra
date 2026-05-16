# Foundation Diagnostic Report

Date: 2026-05-15

## Verified Current State

| Area | Status | Evidence |
| --- | --- | --- |
| Web workspace | active | workspace build, typecheck, and tests |
| API gateway | active | FastAPI smoke endpoints and API tests |
| Host local runtime | active starter | `pnpm local:start`, `local:status`, and `local:stop` manage web/API, local SQLite, and a managed Ollama session when needed |
| PostgreSQL persistence | active starter | refresh tokens and paper orders persist in the local Compose database |
| Market normalization | active starter | canonical `MarketEvent` tests |
| Local Ollama integration | active starter | gateway exposes status, model, and chat endpoints |
| Research reader | active starter | crawler stores paginated readable documents plus source-page trails |
| Visual learning | active starter | deterministic ingestion tests |
| Live broker execution | not started | no active live broker adapter or order-state engine |
| AI broker / agents | not started | workstream docs only |
| Browser automation | active starter | bounded research runs, action logs, provider discovery, and optional Playwright snapshot adapter |
| Mobile / devices | not started | placeholders only |
| Web3 / quantum | not started | research placeholders only |
| Enterprise deployment | not started | roadmap only |

## Confirmed Problems Found

1. The prior Docker stack claimed success while the app container was restarting. The combined container could not find `python`, workspace dependencies were missing, and its healthcheck returned success even while the process failed.
2. Active legacy tests and modules still referenced the removed `src.backend` tree. They created false confidence and were moved to `archive/`.
3. Root architecture docs mixed future-state ideas with implemented behavior. They have been rewritten to separate current runtime from roadmap.
4. The host machine has working Python, Node, Docker, Git, and globally installed `pnpm`.
5. Portfolio data is still mock-local. PostgreSQL is now active for refresh tokens, paper orders, and research documents in Compose, while direct host mode uses persistent local SQLite. Ollama is integrated when reachable, while Redis and Qdrant remain infrastructure starters rather than integrated product dependencies.
6. An earlier Docker verification pass exposed a transient host-runtime problem where several health checks timed out. The later verification pass showed the Compose services healthy again, so Docker is usable but should still be treated as integration infrastructure rather than the only private-development path.
7. Local Ollama is installed and reachable, but CPU inference on `llama3.2:3b` took several minutes for a trivial prompt. That is acceptable for local experiments, not yet acceptable for agent-style interactive workflows.
8. The initial frontend bundle was too large for a first load. Route-level lazy loading plus vendor chunking reduced the entry chunk from about 912 kB to about 72 kB.
9. Docker Desktop Kubernetes, not Veyra, was the main background CPU consumer during the high-CPU sample. The local default Docker stack is now leaner, and the web container serves static assets with Nginx instead of a long-running Vite dev server.

## Local Environment Check

| Tool | Verified |
| --- | --- |
| Python | `python` works, `pip` works, and the launcher exposes Python 3.11 and newer |
| Node.js | installed |
| pnpm | installed globally at version `10.0.0` during cleanup |
| Docker | installed and Compose stack rebuilt successfully |
| Gitleaks | installed during cleanup and used for staged secret scanning |
| Git | installed |

The repository target remains Python 3.11+ even though the default host interpreter is newer. That keeps compatibility broader once heavier ML packages are introduced.

## Verification Run

| Check | Result |
| --- | --- |
| `pnpm install` | passed |
| `pnpm typecheck` | passed |
| `pnpm test` | passed |
| `pnpm build` | passed |
| `python -m pytest services/api-gateway/tests services/visual-learning/tests services/crawler/tests services/ai-engine/tests -q` | passed, 21 tests |
| `pnpm audit --audit-level high` | passed |
| `gitleaks git --staged --redact .` | passed |
| `docker compose config --quiet` | passed |
| `docker compose up --build -d` | passed earlier in the run; later `docker compose ps` showed API, web, PostgreSQL, and Redis healthy |
| Host API `GET /health`, `GET /status`, `GET /api/ai/status`, `GET /api/ai/models`, `POST /api/research/crawl`, `POST /api/browser/research` | passed |
| Host web root on alternate port plus paginated page retrieval | passed |
| Default Docker stack after low-CPU change | passed; idle web container measured at 0.00% CPU and about 4.4 MiB memory |

The browser automation plugin could not attach in this desktop session, so UI verification used the successful Vite build plus HTTP checks rather than a browser screenshot.

## Missing Before Public Release

- durable database models and migrations
- real authentication, MFA, RBAC, sessions, audit logs
- provider adapters, retries, quotas, provenance, replay
- event bus, workers, queues, WebSocket fan-out
- portfolio accounting and valuation engine
- paper broker ledger, then guarded live execution
- risk engine, kill switches, approvals, reconciliation
- alerting and notification service
- observability with metrics, traces, logs, and SLOs
- security review, threat model, backup/restore drills
- mobile sync, device constraints, offline behavior
- crawler deduplication, provenance, robots policy, rate limiting, and full browser action control
- legal and data-licensing review

## High-Value Additions That Were Previously Skipped

- replayable event store
- canonical asset taxonomy across public, physical, business, and digital wealth
- experiment registry for research ideas and rejected hypotheses
- model evaluation harness before agent autonomy
- human-in-the-loop execution receipts
- data lineage and licensing metadata
- visual-learning observation contracts
- explicit asset-intelligence boundary for non-listed wealth
- paginated research storage and local AI summarization
- disaster-recovery exercises

## Benchmark Against Mature Products

Mature financial products tend to win by depth, not slogans:

- charting and alert density similar to TradingView
- customizable cross-asset dashboards similar to Koyfin
- broker APIs, paper trading, and operational controls similar to Alpaca
- broad asset coverage and serious trading workflows similar to Interactive Brokers

Veyra is not near those products yet. The useful comparison is a backlog filter: every major capability needs a real data path, tests, monitoring, and failure handling before it counts.

Reference points:

- TradingView features: <https://www.tradingview.com/features/>
- Koyfin dashboards: <https://www.koyfin.com/features/custom-dashboards/>
- Alpaca trading API: <https://docs.alpaca.markets/us/>
- Interactive Brokers API solutions: <https://www.interactivebrokers.com/en/index.php?f=1325>

## Product Principles

- Treat speculative stories as hypotheses, not signals.
- Borrow cinematic inspiration only as interaction design, for example mission-control dashboards, replay rooms, and explainable alerts.
- Keep reversible research separate from irreversible execution.
- Prefer boring reliability over theatrical complexity.
- Make every advanced feature earn its place with benchmarks.

## Alternatives Worth Considering

- PostgreSQL plus TimescaleDB before adding more specialized stores
- NATS or Redis Streams before Kafka-scale complexity
- retrieval plus small fine-tunes before from-scratch LLM training
- read-only Web3 portfolio aggregation before transaction signing
- classical optimization baselines before quantum experiments
- PWA-first mobile delivery before multiple native apps
