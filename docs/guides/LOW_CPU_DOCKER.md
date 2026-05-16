# Low-CPU Docker Guide

## What happened

During verification on 2026-05-16, the largest CPU consumer was not Veyra. The heavy process was Docker Desktop's Kubernetes control-plane container, while the Veyra app containers were each below 1% CPU in the same sample.

## Practical default

For everyday private development, use the direct host runtime:

```bash
pnpm local:start
```

Use Docker only when you need PostgreSQL/Redis integration checks.

## Lean Compose mode

The default Compose stack now starts only the core services:

- `web`
- `api`
- `postgres`
- `redis`

Optional services are profile-gated:

```bash
docker compose --profile vector up -d qdrant
docker compose --profile tools up -d adminer
```

The core containers also have conservative CPU and memory limits. Docker serves the web app as a static Nginx build instead of running the Vite development server, which keeps CPU use low. Use `pnpm local:start` when you need the editable development experience.

## Workaround for Docker Desktop Kubernetes load

If you are not actively using Kubernetes, run:

```powershell
powershell -ExecutionPolicy Bypass -File tools/scripts/docker-low-cpu.ps1 -StopDesktopKubernetes
```

That stops the optional Veyra services plus Docker Desktop Kubernetes helper containers for the current session. Re-enable Kubernetes from Docker Desktop when you actually need the Kubernetes workstream again.
