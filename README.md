# Veyra

Veyra is a private, local-first financial intelligence platform in active development. The current goal is to build the core privately, then add the advanced capabilities you actually want before any public launch.

## Current Focus

- FastAPI gateway for local development
- Canonical market data normalization
- React web control panel
- Portfolio endpoints and database-backed paper trading
- Local Ollama-backed chat endpoints
- Readable web crawling with paginated research documents
- Bounded browser research automation with multi-page crawling
- PostgreSQL-backed local persistence plus Redis infrastructure
- Basic CI checks for the web app, API, and secret scanning

## Repository Layout

```text
apps/
  web/                  Active React/Vite web application
  mobile/               Private pre-public mobile workstream
  desktop/              Private pre-public desktop workstream
services/
  api-gateway/          Active local-first FastAPI gateway
  market-data/          Canonical market event model and provider normalizers
  ai-engine/            Active Ollama integration boundary
  crawler/              Active readable-content crawler and paginator
  browser-automation/   Optional Playwright, Crawl4AI, and browser-use adapters
  agents/               Private pre-public AI agent workstream
  ai-broker/            Model routing, policy, and validation workstream
  execution/            Broker and order-execution workstream
  trading/              Paper-trading domain boundary
  news/                 Planned news-ingestion boundary
  mcp-gateway/          Planned policy-enforced tool boundary
  asset-intelligence/   Broader wealth-domain workstream
  visual-learning/      Visual observation ingestion starter
  device-hub/           Smart-device integration workstream
  web3-gateway/         Web3 integration workstream
research/
  model-lab/            Model evaluation and training research
  quantum-lab/          Experimental quantum research track
infrastructure/
  docker/               Canonical Docker assets
  cloudflare/           Canonical Cloudflare assets
  enterprise/           Enterprise deployment workstream, last in sequence
tools/
  scripts/              Local helpers
  devops/               Reusable operational automation
archive/
  api_app_legacy/       Historical backend prototype catalog, not active runtime
docs/
  architecture/         Workstream ownership and boundaries
  guides/               Setup and private-foundation guidance
  roadmap/              Private pre-public roadmap
  deployment/           Low-cost deployment notes
```

## Local Setup

Install Node.js 22+, Python 3.11+, and pnpm 10.

```bash
pnpm install
python -m pip install -r services/api-gateway/requirements.txt
```

For the normal private desktop-style workflow, start the host runtime with:

```bash
pnpm local:start
```

That command starts:

- the web app on `http://127.0.0.1:3000`
- the API on `http://127.0.0.1:8000`
- persistent local SQLite storage in `data/veyra_local.db`
- the configured local Ollama connection, defaulting to `http://127.0.0.1:11434`

If Ollama is installed but not already serving, the local runner starts `ollama serve` for the session and stops that managed process when you run `pnpm local:stop`.

Useful local commands:

```bash
pnpm local:status
pnpm local:stop
```

The direct host runtime is the recommended path for private solo development. Docker remains optional integration infrastructure.

Start the web app:

```bash
pnpm --filter @veyra/web dev
```

Start the API:

```bash
cd services/api-gateway
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The local API exposes:

- `GET /health`
- `GET /status`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /api/markets/*`
- `GET /api/portfolio/*`
- `POST/GET/DELETE /api/trading/*`
- `GET /api/ai/status`
- `GET /api/ai/models`
- `POST /api/ai/chat`
- `POST /api/research/crawl`
- `GET /api/research/documents/*`
- `GET /api/browser/providers`
- `POST /api/browser/plan`
- `POST /api/browser/research`

Default local auth credentials are:

```text
email: local@veyra.dev
password: change-me
```

Override them with `VEYRA_DEV_EMAIL` and `VEYRA_DEV_PASSWORD`.

## Private Pre-Public Plan

The intended order is:

1. foundation
2. data, auth, and reliability
3. AI broker and AI agents
4. broker execution
5. mobile and smart-device clients
6. visual learning and broader asset intelligence
7. Web3 and quantum research tracks
8. public release hardening
9. enterprise deployment

See `docs/roadmap/PRIVATE_PHASE_ROADMAP.md`, `docs/architecture/PRE_PUBLIC_WORKSTREAMS.md`, and `docs/reports/FOUNDATION_DIAGNOSTIC_REPORT.md`.
Database choices are documented in `docs/architecture/DATABASE_STRATEGY.md`.

## Optional Docker Infrastructure

The root `docker-compose.yml` starts PostgreSQL, Redis, the API gateway, and the web app for local integration testing.

```bash
docker compose up --build
```

The API uses PostgreSQL in Docker for refresh tokens, paper orders, and research documents. Outside Docker it defaults to persistent local SQLite at `data/veyra_local.db` unless you set `DATABASE_URL`.

The API will use a local Ollama runtime when `OLLAMA_HOST` is reachable. For direct host execution, the default is `http://127.0.0.1:11434`. In Docker, `docker-compose.yml` defaults the API to `http://host.docker.internal:11434` so it can use the Ollama instance already installed on the host. Override `OLLAMA_HOST=http://ollama:11434` if you explicitly start the optional Compose Ollama profile instead.

The default Compose stack is intentionally lean. Qdrant and Adminer are optional profiles, and `docs/guides/LOW_CPU_DOCKER.md` covers the low-CPU workflow when Docker Desktop Kubernetes is not needed.

## Checks

```bash
pnpm typecheck
pnpm test
pnpm build
python -m pytest services/api-gateway/tests services/visual-learning/tests services/crawler/tests services/ai-engine/tests
```

## Security

Do not commit real `.env` files or credentials. Use `.env.example` files for placeholders only, rotate any credentials that were ever committed, and run secret scanning before publishing changes.
