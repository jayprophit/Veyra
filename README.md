# 🌟 Veyra → VRA

**Modular Autonomous Intelligence Platform for Financial Operations**

## Overview

Veyra is a modular autonomous intelligence platform designed for self-hosting, self-improvement, and independence from external AI vendors. Built as a 5-layer system architecture for complete intellectual property ownership and long-term sovereignty.

**Current State:**
- ✅ 5-Layer System Architecture - Core Intelligence, Memory, Self-Improvement, Agent Orchestration, Frontend
- ✅ Self-Hosted AI Infrastructure - Ollama-based with external API fallbacks
- ✅ Multi-Platform Support - Web, mobile, desktop, tablet, smart TV, smart watch, smart glasses, smart devices
- ✅ Service-Oriented Architecture - Modular microservices
- ✅ Event-Driven Design - Decoupled, scalable communication
- ✅ Replaceable Components - Models, databases, brokers, infrastructure
- ✅ Development Ready - CI/CD pipelines and testing infrastructure
---

## Architecture

Veyra follows a monorepo architecture with clear separation of concerns:

```
apps/
  web/            # React web application (control panel)
  mobile/         # Mobile application (control panel)
  desktop/        # Desktop application (control panel)
  tablet/         # Tablet application (control panel)
  smart-tv/       # Smart TV application
  smart-watch/    # Smart watch application
  smart-glasses/  # Smart glasses application
  smart-devices/  # Other smart devices

services/
  api-gateway/      # API gateway and routing
  market-data/      # Market data service
  analytics/        # Analytics service
  auth/             # Authentication service
  alerts/           # Alerts service
  portfolio/        # Portfolio management
  ai-engine/        # AI/ML engine (custom LLM support)
  backtesting/      # Backtesting service
  execution/        # Trade execution

packages/
  ui/              # Shared UI components
  types/           # Shared TypeScript types
  sdk/             # Client SDK
  shared-utils/    # Shared utilities
  config/          # Shared configuration

infrastructure/
  docker/          # Docker configurations
  kubernetes/      # Kubernetes manifests
  terraform/       # Terraform configurations
  cloudflare/      # Cloudflare Workers

tools/
  scripts/         # Utility scripts
  devops/          # DevOps automation

tests/
  integration/     # Integration tests
  e2e/            # End-to-end tests
  performance/    # Performance tests
  security/       # Security tests
```

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Quick Start

### Prerequisites

- Node.js 22+
- pnpm 10+
- Docker (optional, for containerized development)

### Installation

```bash
# Install dependencies
pnpm install

# Start development
pnpm dev

# Run tests
pnpm test

# Build for production
pnpm build
```

### Development

```bash
# Start all services in development mode
pnpm dev

# Start specific app
pnpm --filter @veyra/web dev

# Start specific service
pnpm --filter @veyra/api-gateway dev
```

---

## AI/ML Integration

Veyra supports custom AI/ML models with complete intellectual property ownership:

**Custom LLM Support:**
- Built-from-scratch LLM models (Ollama-based)
- Fine-tuned models for financial analysis
- Hugging Face integration (optional)
- Custom model training pipelines
- Complete IP ownership of all models

**AI Services:**
- Market analysis and prediction
- Portfolio optimization
- Risk assessment
- Sentiment analysis
- Automated trading strategies

**Note:** Third-party LLM APIs (OpenAI, Claude, etc.) are optional. The platform is designed to work primarily with custom, self-hosted models for maximum IP control and cost efficiency.

---

## Deployment

### Development

```bash
pnpm dev
```

### Production

```bash
pnpm build
pnpm start
```

### Docker

```bash
docker-compose up
```

### Cloud Deployment

See [infrastructure/](infrastructure/) for deployment configurations:
- Docker configurations
- Kubernetes manifests
- Terraform scripts
- Cloudflare Workers

---

## Testing

```bash
# Run all tests
pnpm test

# Run integration tests
pnpm --filter @veyra/tests-integration test

# Run E2E tests
pnpm --filter @veyra/tests-e2e test

# Run performance tests
pnpm --filter @veyra/tests-performance test

# Run security tests
pnpm --filter @veyra/tests-security test
```

---

## Security

- **Environment Variables:** Never commit `.env` files
- **Secret Management:** Use proper secret management in production
- **API Keys:** Rotate keys regularly and use environment-specific configurations
- **Authentication:** Implement proper authentication and authorization

See [SECURITY.md](SECURITY.md) for security guidelines.

---

## Roadmap

### Current Phase (Development)
- ✅ Monorepo structure
- ✅ Basic service architecture
- ✅ Web application
- ✅ Testing infrastructure
- 🔄 API gateway implementation
- 🔄 Market data service
- 🔄 Authentication service

### Next Phase (Production Hardening)
- ⏳ Observability (OpenTelemetry, Prometheus, Grafana)
- ⏳ Security hardening
- ⏳ Rate limiting
- ⏳ Audit logging
- ⏳ RBAC implementation
- ⏳ Backup and failover systems

### Future Phase (Financial Infrastructure)
- ⏳ Market data layer
- ⏳ Streaming engine
- ⏳ Risk engine
- ⏳ Portfolio engine
- ⏳ Strategy framework
- ⏳ Backtesting engine
- ⏳ AI infrastructure optimization

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Security](SECURITY.md)
- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)
- [Development Guide](docs/development/)
