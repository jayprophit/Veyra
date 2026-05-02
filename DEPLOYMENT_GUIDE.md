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
