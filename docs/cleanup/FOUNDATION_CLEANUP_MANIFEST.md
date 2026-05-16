# Foundation Cleanup Manifest

This cleanup intentionally narrows the active repository to a local-first foundation while preserving useful private research.

## Removed From Active Tree

- Tracked Python bytecode and `__pycache__` directories
- Duplicate and deployment-heavy GitHub workflows
- npm lockfiles after standardizing on pnpm
- Legacy report/analysis docs that claimed completed production, enterprise, or certification status
- Untracked deployment extras that described a production-ready Kubernetes stack outside the local-first plan
- The untracked `veyra_private_foundation_fixpack` staging folder after its useful files were moved into canonical locations
- The oversized historical backend catalog from the live API gateway package
- Dormant API gateway support code that still referenced the removed backend layout
- Duplicate mobile scaffolding and legacy automation/deployment tooling from the active tree
- Stale integration tests, config bundles, and backend-layout documentation

## Preserved Separately

- Historical backend prototypes now live in `archive/api_app_legacy/`
- Dormant API gateway support code now lives in `archive/api_gateway_legacy/`
- The duplicate Flutter mobile scaffold now lives in `archive/mobile_flutter_legacy/`
- Legacy integration tests now live in `archive/tests_integration_legacy/`
- Legacy config bundles now live in `archive/packages_config_legacy/`
- Legacy backend-layout docs now live in `archive/docs_legacy/`
- Legacy scripts and deployment tooling now live in `archive/tools_legacy/`
- Advanced private work should be rebuilt in the canonical homes listed in `docs/architecture/PRE_PUBLIC_WORKSTREAMS.md`
- Previous deleted tracked content remains recoverable through git history

## Active Runtime

- `apps/web`
- `services/api-gateway`
- `services/market-data`
- `services/visual-learning`
- `docker-compose.yml` for optional local Postgres/Redis integration
