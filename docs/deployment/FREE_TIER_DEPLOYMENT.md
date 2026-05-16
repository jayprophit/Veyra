# Free And Low-Cost Deployment Notes

Use this only after the local foundation is stable.

## Recommended Private Stack

- Frontend: Cloudflare Pages or static hosting
- API: single small VPS, Railway, Render, or Fly.io
- Database: managed Postgres or a local Postgres container for private testing
- Cache/queue: Redis only when async work or streaming needs it
- Object storage: Cloudflare R2
- AI: local Ollama first, paid APIs later behind feature flags
- Monitoring: Prometheus and Grafana when services are actually deployed

## Cost Discipline

Do not optimize for public scale before the core works. Streaming, AI inference, chart refreshes, and market polling can exceed free tiers quickly.

## Deployment Rule

Production should not be created until the project has:

- Passing API and web CI
- Secret scanning
- Environment-specific config
- Auth hardening plan
- Backup and restore plan
- Observability baseline
