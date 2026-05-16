# Pre-Public Workstreams

Veyra has one active foundation and several private pre-public workstreams.

## Active Foundation

- `apps/web`
- `services/api-gateway`
- `services/market-data`
- `services/ai-engine`
- `services/crawler`

## Private Pre-Public Workstreams

| Capability | Canonical Home | Goal Before Public Release |
| --- | --- | --- |
| AI agents | `services/agents` | bounded assistants with policy and audit controls |
| AI broker | `services/ai-broker` | model routing, validation, rate, and budget control |
| Broker execution | `services/execution` | paper first, sandbox second, approved live execution last |
| Browser automation | `services/browser-automation` | local snapshots first, policy-bound task automation later |
| Crawl and research | `services/crawler` | readable extraction, pagination, and provenance |
| Asset intelligence | `services/asset-intelligence` | broader wealth-domain valuation and exposure modeling |
| Visual learning | `services/visual-learning` | validated visual observations before multimodal modeling |
| Model lab | `research/model-lab` | evaluations, retrieval, fine-tuning, and model research |
| Mobile | `apps/mobile` | stable mobile client over the same API contract |
| Smart devices | `services/device-hub` | trusted notification and companion-device layer |
| Quantum | `research/quantum-lab` | reproducible experiments with benchmark evidence |
| Web3 | `services/web3-gateway` | isolated chain integrations with read-only-first behavior |
| Enterprise deployment | `infrastructure/enterprise` | last-stage deployment discipline after public hardening |

## Boundary Rule

The legacy backend catalog in `archive/api_app_legacy/`, dormant API support code in `archive/api_gateway_legacy/`, duplicate Flutter mobile scaffold in `archive/mobile_flutter_legacy/`, archived tests/config/docs, and old tooling in `archive/tools_legacy/` are reference material. New implementation belongs in the canonical home for that capability, with tests and release gates, rather than by reactivating old trees wholesale.

The user wants AI agents, broker execution, mobile, smart devices, quantum, and Web3 achieved before any public launch. That is viable only if each pre-public workstream has a release gate, measurable acceptance criteria, and a clear distinction between:

1. implemented,
2. experimentally validated,
3. production-hardened.
