# Browser Automation

Veyra now has three layers for research browsing:

1. `services/crawler` performs deterministic HTML fetch, readable-text extraction, and pagination.
2. `services/browser-automation` exposes optional adapters for richer automation providers.
3. `services/api-gateway` stores paginated research documents and presents one API contract to the web app.

## Active Today

- HTTP crawling for readable HTML documents.
- Local persistence of research documents.
- Page-by-page retrieval for review.
- Provider discovery for optional browser tools.
- Playwright snapshot adapter when the optional browser dependency is installed.
- Local-model planning endpoint for safe next-step recommendations from visible page text.

## Optional Adapters

| Adapter | Intended Use |
| --- | --- |
| Playwright | direct browser control, rendering, snapshots, deterministic automation |
| Crawl4AI | adaptive crawling, structured extraction, richer research ingestion |
| browser-use | LLM-guided browser tasks with tool control and policy enforcement |

## Release Gate

Agentic browsing is not considered production-ready until it has:

- domain allowlists and deny lists
- human approval for risky actions
- screenshot and DOM audit trails
- rate limiting and timeout control
- deterministic replay fixtures
- safe handling of credentials and downloads
- explicit provenance for every extracted claim
