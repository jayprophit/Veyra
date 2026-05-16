# Private Foundation Start Here

This guide is the entrypoint for turning Veyra into a stable private product before any public release.

## Immediate Goals

1. Keep the active product local-first and private.
2. Make the API gateway runnable with a minimal dependency set.
3. Normalize market data into one canonical model before it reaches UI, AI, or portfolio code.
4. Keep Postgres and Redis optional until local behavior is stable.
5. Separate active runtime code from archived prototypes.

## Active Phase 1 Scope

- Web app
- FastAPI API gateway
- Market data normalizer
- Portfolio endpoints
- Paper-trading endpoints
- Basic CI and secret scanning

## Private Pre-Public Tracks

These are intended before public launch, but each should be built in its canonical home and only promoted when it has tests and release gates:

- AI agents
- AI broker
- Broker execution
- Mobile
- Smart devices
- Quantum research
- Web3 integrations

Enterprise deployment comes after the public-release hardening gate.

## Local Runtime

```bash
pnpm install
python -m pip install -r services/api-gateway/requirements.txt
pnpm --filter @veyra/web dev
```

In another terminal:

```bash
cd services/api-gateway
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
