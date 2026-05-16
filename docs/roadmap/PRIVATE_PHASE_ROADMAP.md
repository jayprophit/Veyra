# Private Phase Roadmap

The product should stay private until the advanced tracks you want are real enough to test together, not merely described in docs.

## Phase 1: Foundation

- Runnable API gateway
- Local web app
- Canonical market data model
- Portfolio endpoints and database-backed paper trading
- Basic local auth
- CI, secret scanning, and reproducible setup

## Phase 2: Data, Auth, And Reliability

- Durable database models and migrations
- Market replay tests
- Portfolio valuation
- Alert rules
- WebSocket streaming prototype
- audit trail, RBAC baseline, backups, and observability starter

## Phase 3: AI Platform

- AI broker for model routing and budgets
- agent runtime with explicit tool policy
- memory integration
- prompt and output validation
- human approval for sensitive actions
- visual-learning ingestion and multimodal evaluation datasets
- model-lab evaluation harness

## Phase 4: Broker And Execution

- paper ledger hardened
- broker sandbox adapters
- reconciliation and cancel/replace flows
- human-approved live broker execution
- strict separation between paper and live modes

## Phase 5: Client Expansion

- mobile app over stable APIs
- push notifications and offline sync
- smart-device companion layer
- lower-bandwidth streaming and device trust

## Phase 6: Frontier Tracks

- Web3 read-only aggregation, then guarded signing paths
- quantum research benchmarks against classical baselines
- only keep experiments that produce measurable value

## Phase 6b: Broader Wealth Domains

- asset-intelligence service boundary
- metals and commodities
- agriculture and food
- property and land
- private businesses and holding-company views
- digital products, services, content, and cashflow

## Phase 7: Public Release Gate

- security review
- recovery drills
- load tests
- support and incident process
- pricing and cost model
- documentation that matches the actual product

## Phase 8: Enterprise Deployment

- multi-tenant controls
- SSO and policy-managed secrets
- environment isolation
- failover, retention, and compliance evidence

## Release Principle

The target before public release is not that every advanced idea is perfect. The target is that the selected private capabilities are real, tested together, and honestly represented.
