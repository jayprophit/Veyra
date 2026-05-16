# Database Strategy

## Primary Store

Use PostgreSQL as Veyra's primary database.

It is the best fit for:

- users and sessions
- orders and trades
- portfolios and positions
- audit records
- transactional consistency
- future relational reporting

The active API uses PostgreSQL for refresh tokens, paper orders, and research documents when run through Docker Compose. When run directly on the host, it defaults to persistent SQLite in `data/veyra_local.db` so private solo development does not depend on Docker.

## Supporting Stores

| Store | Use |
| --- | --- |
| PostgreSQL | source of truth for relational application data |
| Redis | cache, rate limits, queues, pub/sub |
| Qdrant | vector search and retrieval |
| TimescaleDB extension | later time-series workloads on top of PostgreSQL |

## Why Not Add MongoDB Or MySQL Now

- MongoDB is useful for document-heavy workloads, but Veyra's core finance records need relational constraints, joins, and transactions first.
- MySQL can serve many web apps well, but PostgreSQL already covers the needed relational workload and has a better upgrade path into richer SQL, JSON, extensions, and time-series use.
- Adding multiple primary databases early would increase operations cost and duplicate data models without improving the current product.

## Current Local Tables

- `refresh_tokens`
- `paper_orders`
- `research_documents`

## Next Database Work

1. add Alembic migrations
2. add users, portfolios, positions, and audit tables
3. add backup and restore scripts
4. add TimescaleDB only when real market-history storage arrives
