# Financial Master - Live Deployment Guide

=========================================

## 🚀 **NEW: Automated Infrastructure Setup (30 seconds)**

### One Command to Start Everything

```powershell
# Option A: Start Docker + WSL + Financial Master
.\START_HERE.ps1 -QuickStart

# Option B: Start with AI/Ollama integration
.\START_HERE.ps1 -WithAI

# Check infrastructure status
.\START_HERE.ps1 -Status

# Stop all services
.\START_HERE.ps1 -Stop
```

### What Gets Automated

- ✅ **Docker Desktop** - Starts if not running (Windows)
- ✅ **WSL2 Ubuntu** - Starts/initializes if needed
- ✅ **Ollama** - Local AI models (llama3.2, mistral)
- ✅ **PostgreSQL + Redis** - Via Docker Compose
- ✅ **Financial Master Stack** - API + Frontend

### Linux/WSL Commands

```bash
# Full automated setup
./scripts/automate_infrastructure.sh start

# With system optimization for AI
./scripts/automate_infrastructure.sh setup

# Stop all services
./scripts/automate_infrastructure.sh stop
```

---

## Quick Start: Go Live in 15 Minutes (FREE)

### Option 1: Local Testing (Immediate)

```powershell
# 1. Copy environment file
copy .env.local .env

# 2. Add your free API keys to .env:
# - Alpaca Paper Trading (https://alpaca.markets)
# - Finnhub (https://finnhub.io)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the API server
uvicorn src.backend.app.api_server:app --reload --port 8000

# 5. Start WebSocket feeds (new terminal)
python src/backend/app/websocket_real_time_feeds.py

# 6. Verify it's working
curl http://localhost:8000/api/health
```

### Option 2: Cloud Deployment (Staging)

#### Step 1: Push to GitHub

```powershell
git add .
git commit -m "Add deployment configs"
git push origin main
```

#### Step 2: Deploy to Render (Free)

1. Go to <https://render.com>
2. Click "New Web Service"
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml`
5. Set environment variables in dashboard:
   - `ALPACA_PAPER_API_KEY`
   - `ALPACA_PAPER_API_SECRET`
   - `FINNHUB_API_KEY`

#### Step 3: Add Cloudflare Workers (API Gateway)

```bash
cd cloudflare
npm install -g wrangler
wrangler login
wrangler deploy
```

---

## Free API Keys You Need

| Service | Purpose | Get Key At | Free Tier |
|---------|---------|------------|-----------|
| **Alpaca** | Paper Trading | <https://alpaca.markets> | Unlimited paper trades |
| **Finnhub** | Real-time US stocks | <https://finnhub.io> | 60 calls/min |
| **Polygon** | Market data | <https://polygon.io> | 5 calls/min |
| **Alpha Vantage** | Stock fundamentals | <https://alphavantage.co> | 25 calls/day |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE (Free)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Workers  │  │   Pages    │  │    R2      │           │
│  │  API Gateway│  │   Docs     │  │  Storage   │           │
│  │  Rate Limit │  │  Hosting   │  │            │           │
│  └──────┬──────┘  └─────────────┘  └─────────────┘           │
└─────────┼─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    RENDER (Free)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           FastAPI Backend (Python)                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │    API      │  │   Agents    │  │  WebSocket  │  │   │
│  │  │   Server    │  │             │  │   Feeds     │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           NEON PostgreSQL (Free 500MB)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              BROKER APIs (Paper Trading)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Alpaca   │  │  Interactive │  │   Trading  │           │
│  │   Paper    │  │   Brokers    │  │     212    │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Ollama AI Integration (Local LLMs - FREE)

### Quick Start with AI

```powershell
# Start everything including Ollama
.\START_HERE.ps1 -WithAI

# Or manually manage Ollama
.\scripts\automate_infrastructure.ps1 -StartOllama
.\scripts\setup_ollama_models.ps1 -PullRecommended
```

### Docker Compose with Ollama

```bash
# Start with AI services
$env:COMPOSE_PROFILES="ai"
docker-compose -f docker-compose.yml -f docker-compose.ollama.yml up -d

# Or explicitly
$env:COMPOSE_PROFILES="full"
docker-compose -f docker-compose.yml -f docker-compose.ollama.yml up -d
```

### Available Profiles

| Profile | Services | Use Case |
|---------|----------|----------|
| `default` | API, DB, Redis, Frontend | Basic setup |
| `ai` | + Ollama container | AI analysis features |
| `full` | + Monitoring (Prometheus/Grafana) | Complete stack |
| `monitoring` | Prometheus + Grafana only | Just monitoring |

### Recommended Models

Run `.\scripts\setup_ollama_models.ps1 -PullRecommended` to install:

- **llama3.2:3b** - Fast summaries, simple Q&A (~2GB)
- **llama3.1:8b** - Complex analysis, reports (~5GB)
- **mistral:7b** - Good balance of speed/quality (~4GB)
- **codellama:7b** - Code/data processing (~4GB)

### Testing AI Features

```bash
# Test Ollama is running
curl http://localhost:11434/api/tags

# Test Financial Master AI endpoint
curl http://localhost:8000/api/v1/ai/analyze -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze AAPL stock"}'
```

---

## Testing Checklist

### Local Testing

- [ ] `curl http://localhost:8000/api/health` returns `{"status": "healthy"}`
- [ ] `curl http://localhost:8000/api/portfolio/summary` returns portfolio data
- [ ] WebSocket connects at `ws://localhost:8765`
- [ ] Mock data is streaming (check logs)

### Paper Trading Testing

- [ ] Alpaca paper account has $100k virtual cash
- [ ] Place test buy order via API
- [ ] Verify order appears in Alpaca dashboard
- [ ] Place test sell order
- [ ] Verify positions update correctly

### Cloud Testing

- [ ] Render deployment shows "Your service is live"
- [ ] Cloudflare Workers route requests correctly
- [ ] Database connects without errors
- [ ] All endpoints return expected data

---

## Environment Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `.env.local` | Local dev with mock data | Daily development |
| `.env.staging` | Cloud testing with real data | Pre-production testing |
| `.env.production` | Live trading (real money) | Only when 100% ready |

---

## Infrastructure Tools & Orchestration

Financial Master supports multiple deployment patterns from local development to production-scale Kubernetes clusters.

### Container Orchestration Matrix

| Tool | Purpose | Status | Priority | When to Use |
|------|---------|--------|----------|-------------|
| **Docker** | Container runtime | ✅ Active | High | Local development, simple deployments |
| **Docker Compose** | Multi-container local orchestration | ✅ Active | High | Full stack on single machine |
| **Kubernetes** | Production container orchestration | ✅ Configured | High | Scalable production workloads |
| **Helm** | Kubernetes package management | ✅ Available | Medium | Managing K8s app lifecycle |
| **GitHub Actions** | CI/CD automation | ✅ Active | High | Automated testing & deployment |
| **Terraform** | Infrastructure as Code | ⏳ Optional | Low | AWS/GCP/Azure provisioning |
| **Istio** | Service mesh | ⏭️ Future | Skip | Not needed at current scale |
| **ArgoCD** | GitOps continuous delivery | ⏳ Optional | Low | Advanced K8s deployment patterns |

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT (Local)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Docker     │  │  Docker     │  │   Redis     │           │
│  │  Compose    │  │  Compose    │  │             │           │
│  │  (API)      │  │  (Frontend) │  │             │           │
│  └──────┬──────┘  └─────────────┘  └─────────────┘           │
└─────────┼─────────────────────────────────────────────────────┘
          │
          ▼ Docker Build
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD (GitHub Actions)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │    Test     │  │    Build    │  │    Push     │           │
│  │   (pytest)  │  │   (Docker)  │  │  (GHCR)     │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
          │
          ▼ Helm Deploy
┌─────────────────────────────────────────────────────────────┐
│                    STAGING / PRODUCTION                      │
│                    (Kubernetes Cluster)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Helm      │  │  K8s        │  │  HPA        │           │
│  │  Release    │  │  Ingress    │  │  Autoscale  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Helm Deployment (Recommended for K8s)

#### Quick Start

```bash
# Install Financial Master with Helm
helm install financial-master ./helm/financial-master \
  --namespace financial-master \
  --create-namespace \
  --set global.environment=staging

# Verify deployment
kubectl get pods -n financial-master
kubectl get ingress -n financial-master

# Upgrade deployment
helm upgrade financial-master ./helm/financial-master \
  --namespace financial-master \
  --set api.image.tag=v4.0.1
```

#### Environment-Specific Values

```bash
# Development (minimal resources)
helm install financial-master ./helm/financial-master \
  --namespace financial-master-dev \
  --create-namespace \
  -f ./helm/financial-master/values.yaml \
  --set api.replicaCount=1 \
  --set api.autoscaling.enabled=false \
  --set postgresql.primary.persistence.enabled=false

# Production (full scale)
helm install financial-master ./helm/financial-master \
  --namespace financial-master-prod \
  --create-namespace \
  -f ./helm/financial-master/values.yaml \
  --set api.replicaCount=5 \
  --set api.autoscaling.maxReplicas=20 \
  --set global.environment=production
```

### Raw Kubernetes Manifests

For environments without Helm:

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

### CI/CD Pipeline

The GitHub Actions workflow (`ci-cd.yml`) includes:

1. **Test Stage** - Python 3.10/3.11/3.12 matrix testing
2. **Lint Stage** - Code quality checks (flake8, black, isort)
3. **Security Stage** - Bandit security scanning
4. **Build Stage** - Docker image build & push to GitHub Container Registry
5. **Deploy Stage** - Automated Helm deployment to staging

**Required Secrets**:

- `KUBE_CONFIG_STAGING` - Base64-encoded kubeconfig for staging cluster
- `GITHUB_TOKEN` - Auto-provided for GHCR authentication

### Monitoring & Observability

| Component | Tool | Access |
|-----------|------|--------|
| Metrics | Prometheus | `kubectl port-forward svc/prometheus 9090` |
| Dashboards | Grafana | `kubectl port-forward svc/grafana 3000` |
| Health | Liveness/Readiness | `/api/v1/health`, `/api/v1/ready` |
| Scaling | HPA | `kubectl get hpa -n financial-master` |
| Logs | kubectl | `kubectl logs -f deployment/fm-api` |

---

## Safety Features

Your setup has these protections:

1. **Paper Trading Required** in staging (`ALPACA_PAPER=true`)
2. **Trade Limits** (`MAX_DAILY_TRADES=5`)
3. **Approval Threshold** (`APPROVAL_THRESHOLD=$10,000`)
4. **Kill Switch** (`ENABLE_KILL_SWITCH=true`)
5. **Rate Limiting** (60 req/min via Cloudflare)

---

## Troubleshooting

### Render deployment fails

```bash
# Check logs in Render dashboard
# Common issues:
# 1. Missing environment variables
# 2. Database connection string wrong
# 3. Python version mismatch
```

### Can't connect to Alpaca

```bash
# Test Alpaca connection
curl -H "APCA-API-KEY-ID: YOUR_KEY" \
     -H "APCA-API-SECRET-KEY: YOUR_SECRET" \
     https://paper-api.alpaca.markets/v2/account
```

### Database errors

```bash
# Test Neon connection
psql "YOUR_NEON_CONNECTION_STRING" -c "SELECT NOW();"
```

---

## Next Steps After Deployment

1. **Add monitoring**: Sentry for errors, UptimeRobot for uptime
2. **Set up notifications**: Telegram bot for trade alerts
3. **Configure backups**: Automated database backups
4. **Document API**: Auto-generated docs at `/docs`
5. **Test strategies**: Run backtests with paper trading

---

## Costs

| Component | Service | Monthly Cost |
|-----------|---------|-------------|
| Backend | Render | $0 (free tier) |
| Database | Neon | $0 (500MB free) |
| API Gateway | Cloudflare Workers | $0 (100k req/day) |
| Docs Hosting | Cloudflare Pages | $0 (unlimited) |
| Monitoring | UptimeRobot | $0 (50 monitors) |
| **TOTAL** | | **$0/month** |

---

## Support

- **Alpaca Paper Trading**: <https://alpaca.markets/support>
- **Render Help**: <https://render.com/docs>
- **Cloudflare Workers**: <https://developers.cloudflare.com/workers/>
