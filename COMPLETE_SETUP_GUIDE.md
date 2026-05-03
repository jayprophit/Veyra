# Financial Master - Complete Setup & Deployment Guide

## World-Class Industrial Build | Free Tier + Open Source

---

## TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [Free Tier Services Stack](#free-tier-services-stack)
3. [Required APIs & Sign-Up Links](#required-apis--sign-up-links)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [Local Development Setup](#local-development-setup)
6. [Cloud Deployment](#cloud-deployment)
7. [Infrastructure & Kubernetes](#infrastructure--kubernetes)
8. [Testing Strategy](#testing-strategy)
9. [GDPR & Data Compliance](#gdpr--data-compliance)
10. [Security Configuration](#security-configuration)
11. [Monitoring & Maintenance](#monitoring--maintenance)

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER DEVICES                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Laptop  │  │ Desktop │  │ Mobile  │  │ Tablet  │  │  Other  │   │
│  │(Windsurf)│  │(Ollama) │  │ (App)   │  │ (Web)   │  │(Smart)  │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       └─────────────┴─────────────┴─────────────┴─────────────┘     │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │           LOCAL SQLITE DATABASE (GDPR Compliant)            │    │
│  │     All personal financial data stored on user's device     │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Sync (optional, encrypted)
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CLOUD SERVICES                               │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   GitHub     │◄──►│  Cloudflare  │◄──►│   Render     │          │
│  │  (Code Repo) │    │  (CDN/DNS)   │    │  (Backend)   │          │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘          │
│                             │                   │                  │
│                             ▼                   ▼                  │
│                      ┌──────────────┐    ┌──────────────┐          │
│                      │    Neon      │    │    R2        │          │
│                      │  (Database)  │    │  (Storage)   │          │
│                      └──────────────┘    └──────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL APIs                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐     │
│  │   Alpaca   │ │   Polygon  │ │AlphaVantage│ │    FRED    │     │
│  │  (Trading) │ │  (Stocks)  │ │ (Stocks)   │ │ (Economy)  │     │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐     │
│  │  Coinbase  │ │  Yahoo Fin │ │   OpenAI   │ │  Ollama    │     │
│  │  (Crypto)  │ │  (Free)    │ │  (AI/ML)   │ │  (Local)   │     │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## FREE TIER SERVICES STACK

| Component | Service | Cost | Limits | Upgrade Path |
|-----------|---------|------|--------|--------------|
| **Code Repo** | GitHub | FREE | Unlimited repos, 2000 CI min/mo | Pro $4/mo |
| **Frontend/Docs** | Cloudflare Pages | FREE | Unlimited sites, 1 build/min | Pro $20/mo |
| **Backend** | Render | FREE | Web services, spins down after 15min | Starter $7/mo |
| **Database** | Neon PostgreSQL | FREE | 500MB storage, 190 compute hrs/mo | Pro $19/mo |
| **Storage** | Cloudflare R2 | FREE | 10GB storage, 10M reads/mo | Pay per use |
| **API Gateway** | Cloudflare Workers | FREE | 100,000 requests/day | $5/10M requests |
| **Monitoring** | UptimeRobot | FREE | 50 monitors, 5min checks | Pro $8/mo |
| **Secrets** | GitHub Secrets | FREE | Unlimited repos | - |
| **Domain** | Cloudflare Registrar | ~$8/yr | Domain registration | - |
| **Error Tracking** | Sentry | FREE | 5000 errors/mo, 1 user | Team $26/mo |

**Total Monthly Cost: $0** (until you need to scale)

---

## REQUIRED APIs & SIGN-UP LINKS

### 1. Market Data APIs (Free Tier)

| API | Purpose | Free Tier | Sign Up | Rate Limits |
|-----|---------|-----------|---------|-------------|
| **Alpaca** | Paper Trading + Data | $0 | [alpaca.markets](https://alpaca.markets) | 200 requests/min |
| **Polygon.io** | Real-time US stocks | $0 (test key) | [polygon.io](https://polygon.io) | 5 API calls/min |
| **Alpha Vantage** | Stock data backup | 25 calls/day | [alphavantage.co](https://www.alphavantage.co) | 5 calls/min |
| **Yahoo Finance** | Free data (unofficial) | Unlimited | `yfinance` Python lib | No limits |
| **FRED** | Economic data | 120 requests/day | [fred.stlouisfed.org](https://fred.stlouisfed.org) | No key needed |

### 2. Crypto APIs (Free Tier)

| API | Purpose | Free Tier | Sign Up |
|-----|---------|-----------|---------|
| **Coinbase Pro** | Trading + Data | $0 | [pro.coinbase.com](https://pro.coinbase.com) |
| **Binance API** | Data + Spot trading | $0 | [binance.com](https://binance.com) |
| **CryptoCompare** | Price data | 100k calls/mo | [cryptocompare.com](https://min-api.cryptocompare.com) |
| **CoinGecko** | Price + Market data | 10-30 calls/min | [coingecko.com](https://www.coingecko.com) |

### 3. AI/ML Services (Free Tier)

| Service | Purpose | Free Tier | Sign Up |
|---------|---------|-----------|---------|
| **OpenAI** | GPT-4 for analysis | $5 credit | [platform.openai.com](https://platform.openai.com) |
| **Hugging Face** | Open source models | $0 (inference API) | [huggingface.co](https://huggingface.co) |
| **Ollama** | Local LLMs | $0 (self-hosted) | [ollama.ai](https://ollama.ai) |
| **Groq** | Fast inference | $0 (credits) | [groq.com](https://groq.com) |

### 4. Optional Services

| Service | Purpose | Free Tier | Sign Up |
|---------|---------|-----------|---------|
| **Plaid** | Bank account sync | Sandbox free | [plaid.com](https://plaid.com) |
| **Telegram Bot** | Notifications | $0 | [@BotFather](https://t.me/botfather) |
| **Sentry** | Error tracking | 5000 errors/mo | [sentry.io](https://sentry.io) |
| **Infura** | Ethereum node | 100k requests/day | [infura.io](https://infura.io) |

---

## STEP-BY-STEP SETUP

### Phase 1: Account Creation (30 minutes)

#### 1.1 GitHub Setup

```bash
# 1. Create GitHub account (if not done)
# https://github.com/signup

# 2. Create new repository
# https://github.com/new
# Name: Financial-Master
# Visibility: Private (for security)

# 3. Add repository secrets (will do later)
# Settings > Secrets and variables > Actions
```

#### 1.2 Cloudflare Setup

```bash
# 1. Sign up for Cloudflare (hobbyist free account)
# https://dash.cloudflare.com/sign-up

# 2. Add your domain or get free subdomain:
# - Pages.dev subdomain: your-project.pages.dev
# - Or register domain: ~$8/year via Cloudflare

# 3. Create R2 bucket:
# Storage & Images > R2 > Create bucket
# Name: financial-master-storage
# Location: Automatic
```

#### 1.3 Render Setup

```bash
# 1. Sign up for Render
# https://render.com
# (Use GitHub login for easy integration)

# 2. No credit card required for free tier
```

#### 1.4 Neon Database Setup

```bash
# 1. Sign up for Neon
# https://neon.tech

# 2. Create project:
# - Name: financial-master
# - Region: Choose closest to you (EU: Frankfurt, US: Ohio)

# 3. Get connection string:
# Dashboard > Connection String > copy URI
```

#### 1.5 UptimeRobot Setup

```bash
# 1. Sign up for UptimeRobot
# https://uptimerobot.com

# 2. Add monitor (will do after deployment)
```

---

### Phase 2: API Key Acquisition (45 minutes)

#### 2.1 Alpaca (Paper Trading)

```bash
# 1. Visit: https://app.alpaca.markets/signup
# 2. Verify email
# 3. Go to Paper Trading dashboard
# 4. Generate API Keys:
#    Paper Trading > Generate Keys
#    - API Key ID: copy to clipboard
#    - Secret Key: copy to clipboard (shown once!)

# 5. Save for later:
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

#### 2.2 Polygon.io

```bash
# 1. Visit: https://polygon.io/dashboard/signup
# 2. Verify email
# 3. Get free API key:
#    Dashboard > API Keys > Create Key

# 4. Save for later:
POLYGON_API_KEY=your_key_here
```

#### 2.3 Alpha Vantage

```bash
# 1. Visit: https://www.alphavantage.co/support/#api-key
# 2. Enter email
# 3. Copy API key from email

# 4. Save for later:
ALPHA_VANTAGE_API_KEY=your_key_here
```

#### 2.4 OpenAI (Optional - for AI features)

```bash
# 1. Visit: https://platform.openai.com/signup
# 2. Add payment method for $5 free credit
# 3. Create API key:
#    API Keys > Create new secret key

# 4. Save for later:
OPENAI_API_KEY=your_key_here
```

#### 2.5 Telegram Bot (Optional - for notifications)

```bash
# 1. Message @BotFather on Telegram
# 2. Type: /newbot
# 3. Name your bot: FinancialMasterBot
# 4. Get token (save this!)

# 5. Get your chat ID:
#    Message @userinfobot

# 6. Save for later:
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

---

### Phase 3: Local Environment Setup (30 minutes)

#### 3.1 Prerequisites

```bash
# Windows (PowerShell as Administrator):

# Install Python 3.11+
winget install Python.Python.3.11

# Install Node.js 18+
winget install OpenJS.NodeJS

# Install Git
winget install Git.Git

# Install Ollama (local LLM)
winget install Ollama.Ollama

# Verify installations
python --version  # 3.11.x
node --version  # v18.x.x
git --version   # 2.x.x
ollama --version
```

#### 3.2 Clone Repository & Setup

```powershell
# Navigate to your project
cd "c:\Users\jpowe\Desktop\Financial Master"

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env
```

#### 3.3 Configure Local Environment File

Edit `c:\Users\jpowe\Desktop\Financial Master\.env`:

```env
# ============================================================================
# DATA PROVIDERS - Fill in your API keys
# ============================================================================

# Polygon.io - Real-time US stock data
POLYGON_API_KEY=your_polygon_api_key_here

# Alpaca - Trading execution (PAPER TRADING for testing)
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Alpha Vantage - Backup market data
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Coinbase Pro - Crypto trading (optional)
# COINBASE_API_KEY=your_coinbase_key
# COINBASE_SECRET=your_coinbase_secret

# ============================================================================
# DATABASE - Local SQLite for GDPR compliance
# ============================================================================
DATABASE_URL=sqlite:///data/financial_master.db

# ============================================================================
# SECURITY - Generate strong random keys
# ============================================================================

# Generate JWT secret (run in PowerShell):
# [System.Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 } | ForEach-Object { [byte]$_ }))
JWT_SECRET_KEY=your_generated_jwt_secret_here

# Generate encryption key (32 bytes):
# [System.Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 } | ForEach-Object { [byte]$_ }))
ENCRYPTION_KEY=your_generated_encryption_key_here

# ============================================================================
# FEATURE FLAGS - For testing phase
# ============================================================================
DATA_SOURCE=mock  # Change to 'live' after API keys configured
ENABLE_PAPER_TRADING=true
ENABLE_REAL_TRADING=false  # NEVER enable for testing
ENABLE_WEBSOCKET=true
ENABLE_AI_ANALYSIS=true

# ============================================================================
# MONITORING (optional)
# ============================================================================
# SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO

# ============================================================================
# AI SERVICES (optional)
# ============================================================================
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key

# ============================================================================
# TELEGRAM NOTIFICATIONS (optional)
# ============================================================================
# TELEGRAM_BOT_TOKEN=your_bot_token
# TELEGRAM_CHAT_ID=your_chat_id

# ============================================================================
# DEVELOPMENT
# ============================================================================
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
FRONTEND_URL=http://localhost:3000
```

#### 3.4 Test Local Setup

```powershell
# Ensure you're in the project directory and venv is activated
cd "c:\Users\jpowe\Desktop\Financial Master"
.venv\Scripts\Activate.ps1

# Run validation
python -m src.backend.app.validate_setup

# Start the backend
python -m src.backend.app.main

# Or use the autonomous controller
python -m src.backend.app.autonomous_master_controller

# Test API is running
curl http://localhost:8000/health
```

---

## LOCAL DEVELOPMENT SETUP

### Directory Structure

```
c:\Users\jpowe\Desktop\Financial Master\
├── .venv/                          # Python virtual environment
├── .git/                           # Git repository
├── .github/                        # GitHub Actions workflows
├── .windsurf/                      # Windsurf IDE settings
├── cloudflare/                     # Cloudflare Workers
├── config/                         # Docker, nginx configs
├── data/                           # Local SQLite database
├── docs/                           # Documentation
├── frontend/                       # React frontend
├── mobile/                         # Flutter mobile app
├── scripts/                        # Automation scripts
├── src/
│   ├── backend/                    # Python backend
│   ├── frontend/                   # Frontend components
│   └── shared/                     # Shared code
├── tests/                          # Test suites
├── .env                            # Environment variables (local)
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
└── README.md                       # Project readme
```

### Development Workflow

```powershell
# 1. Start local development
# Open PowerShell in project folder

cd "c:\Users\jpowe\Desktop\Financial Master"

# 2. Activate virtual environment
.venv\Scripts\Activate.ps1

# 3. Start backend server
python -m src.backend.app.main

# 4. In new terminal, start frontend
cd frontend
npm install
npm start

# 5. Access applications
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

---

## CLOUD DEPLOYMENT

### Phase 4: Deploy to Render (Backend)

#### 4.1 Create Web Service

```
1. Go to https://dashboard.render.com
2. Click "New +" > "Web Service"
3. Connect your GitHub repository: jayprophit/Financial-Master
4. Configure:
   - Name: financial-master-api
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn src.backend.app.main:app --host 0.0.0.0 --port 10000
   - Plan: Free

5. Add Environment Variables (all from your .env file):
   - POLYGON_API_KEY
   - ALPACA_API_KEY
   - ALPACA_SECRET_KEY
   - ALPACA_BASE_URL
   - ALPHA_VANTAGE_API_KEY
   - DATABASE_URL (use Neon connection string)
   - JWT_SECRET_KEY
   - ENCRYPTION_KEY
   - DATA_SOURCE=live
   - ENABLE_PAPER_TRADING=true
   - ENABLE_REAL_TRADING=false
   - ENABLE_WEBSOCKET=true

6. Click "Create Web Service"
7. Wait for deployment (5-10 minutes)
8. Copy the deployed URL: https://financial-master-api.onrender.com
```

### Phase 5: Deploy to Neon (Database)

#### 5.1 Configure Neon Database

```
1. Go to https://console.neon.tech
2. Select your project: financial-master
3. Get connection string:
   Dashboard > Connection Details > copy "PostgreSQL URL"
   
4. Update Render environment variable:
   DATABASE_URL=postgresql://user:pass@host.neon.tech/financial-master
   
5. Test connection from local:
   psql $DATABASE_URL
```

### Phase 6: Deploy to Cloudflare Pages (Frontend/Docs)

#### 6.1 Deploy Documentation

```
1. Go to https://dash.cloudflare.com
2. Pages > Create a project > Connect to Git
3. Select: jayprophit/Financial-Master
4. Configure:
   - Project name: financial-master-docs
   - Production branch: main
   - Build command: (none - static files)
   - Root directory: docs/
   
5. Click "Save and Deploy"
6. Your docs will be at: https://financial-master-docs.pages.dev
```

#### 6.2 Deploy Frontend (if React build)

```
1. Pages > Create a project > Connect to Git
2. Select: jayprophit/Financial-Master
3. Configure:
   - Project name: financial-master-app
   - Production branch: main
   - Build command: cd frontend && npm install && npm run build
   - Output directory: frontend/dist
   
4. Add environment variables:
   - VITE_API_URL=https://financial-master-api.onrender.com
   
5. Click "Save and Deploy"
```

### Phase 7: Configure Cloudflare Workers (API Gateway)

#### 7.1 Deploy Workers

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Navigate to cloudflare folder
cd "c:\Users\jpowe\Desktop\Financial Master\cloudflare"

# Install dependencies
npm install

# Deploy
wrangler deploy

# Your worker will be at:
# https://financial-master-api.your-account.workers.dev
```

---

## INFRASTRUCTURE & KUBERNETES

### Container Orchestration Stack

Financial Master supports multiple deployment patterns from local development to production-scale Kubernetes clusters.

| Tool | Purpose | Status | Priority | When to Use |
|------|---------|--------|----------|-------------|
| **Docker** | Container runtime for local development | ✅ Active | High | Local development, simple deployments |
| **Docker Compose** | Multi-container orchestration | ✅ Active | High | Full stack on single machine |
| **Kubernetes** | Production container orchestration | ✅ Configured | High | Scalable production workloads |
| **Helm** | K8s package management | ✅ Available | Medium | Managing K8s app lifecycle |
| **GitHub Actions** | CI/CD automation | ✅ Active | High | Automated testing & deployment |
| **Terraform** | Infrastructure as Code | ⏳ Optional | Low | AWS/GCP/Azure provisioning |
| **Istio** | Service mesh | ⏭️ Future | Skip | Not needed at current scale |
| **ArgoCD** | GitOps continuous delivery | ⏳ Optional | Low | Advanced K8s deployment patterns |

### Local Development with Docker

```bash
# Start full stack with monitoring
docker-compose up -d

# Access services:
# - API: http://localhost:8000
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
# - Ollama (AI): http://localhost:11434

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

### Kubernetes Deployment

#### Option 1: Helm (Recommended)

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

#### Option 2: Raw Kubernetes Manifests

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

### Environment-Specific Helm Values

```bash
# Development (minimal resources)
helm install financial-master ./helm/financial-master \
  --namespace financial-master-dev \
  --create-namespace \
  --set api.replicaCount=1 \
  --set api.autoscaling.enabled=false \
  --set postgresql.primary.persistence.enabled=false

# Production (full scale)
helm install financial-master ./helm/financial-master \
  --namespace financial-master-prod \
  --create-namespace \
  --set api.replicaCount=5 \
  --set api.autoscaling.maxReplicas=20 \
  --set global.environment=production
```

### CI/CD Pipeline

Every push to `main` automatically triggers:

1. **Test** - Python 3.10/3.11/3.12 matrix testing
2. **Lint** - Code quality checks (flake8, black, isort)
3. **Security** - Bandit security scanning
4. **Build** - Docker image build & push to GitHub Container Registry
5. **Deploy** - Automated Helm deployment to staging Kubernetes cluster

Required GitHub Secrets:

- `KUBE_CONFIG_STAGING` - Base64-encoded kubeconfig for staging cluster
- `GITHUB_TOKEN` - Auto-provided for GHCR authentication

### Monitoring Stack

- **Prometheus** - Metrics collection at `http://localhost:9090`
- **Grafana** - Dashboards at `http://localhost:3000` (admin/admin)
- **Health Checks** - `/api/v1/health` (liveness), `/api/v1/ready` (readiness)
- **HPA** - Horizontal Pod Autoscaler (3-10 replicas based on CPU/memory)

---

## TESTING STRATEGY

### Mock Data Testing (Week 1-2)

```powershell
# Use mock data to test all features
.venv\Scripts\Activate.ps1
$env:DATA_SOURCE="mock"
python -m src.backend.app.main

# Test all endpoints:
curl http://localhost:8000/api/v1/market/quote/BTC-USD
curl http://localhost:8000/expenses/summary/monthly/2026/4
curl http://localhost:8000/wealth/total

# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v
```

### Paper Trading Testing (Week 3-4)

```powershell
# Switch to paper trading with live data
# Edit .env:
DATA_SOURCE=live
ENABLE_PAPER_TRADING=true
ENABLE_REAL_TRADING=false

# Restart and test
python -m src.backend.app.main

# Execute paper trades via API:
curl -X POST http://localhost:8000/api/v1/order \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 1,
    "order_type": "market",
    "broker": "alpaca"
  }'

# Monitor paper trading performance daily
# Goal: 75%+ success rate on signals
```

### Live Data Backtesting (Week 5-8)

```powershell
# Run backtesting with 1-2 years historical data
python -m src.backend.app.backtesting.engine \
  --start-date 2024-01-01 \
  --end-date 2025-04-30 \
  --strategy all \
  --report

# Analyze results
# Goal: >75% profitable trades, Sharpe >1.5
```

### Performance Metrics to Track

| Metric | Target | Minimum | Measurement |
|--------|--------|---------|-------------|
| Win Rate | 80% | 75% | % profitable trades |
| Profit Factor | 2.0 | 1.5 | Gross profit / gross loss |
| Sharpe Ratio | 2.0 | 1.5 | Risk-adjusted return |
| Max Drawdown | <10% | <15% | Peak to trough decline |
| Recovery Factor | 3.0 | 2.0 | Net profit / max drawdown |

---

## GDPR & DATA COMPLIANCE

### Data Storage Strategy

| Data Type | Storage Location | Reason |
|-----------|------------------|--------|
| Personal financial data | Local SQLite | GDPR compliance, user control |
| Market data | Cloud (cached) | Public data, performance |
| Trading history | Local + optional cloud backup | User ownership |
| API keys | GitHub Secrets / .env local | Security |
| Analytics/telemetry | Anonymized cloud | Performance monitoring |

### GDPR Compliance Checklist

- [ ] **Data Minimization**: Only store necessary data locally
- [ ] **Consent**: Clear privacy policy on first run
- [ ] **Right to Access**: Export all user data feature
- [ ] **Right to Erasure**: Delete all local data feature
- [ ] **Data Portability**: JSON export/import functionality
- [ ] **Security**: Encrypted local database
- [ ] **Breach Notification**: Automated alerts

### Implementation

```python
# Local data encryption (already in codebase)
from cryptography.fernet import Fernet

# Generate key (one-time setup)
# key = Fernet.generate_key()

# Encrypt sensitive fields
cipher = Fernet(ENCRYPTION_KEY)
encrypted = cipher.encrypt(sensitive_data.encode())
```

---

## SECURITY CONFIGURATION

### Required Security Measures

#### 1. API Key Rotation Schedule

```
Alpaca:         Rotate every 90 days
Polygon:        Rotate every 180 days
Alpha Vantage:  Rotate every 180 days
OpenAI:         Rotate every 90 days
JWT Secret:     Rotate every 30 days
```

#### 2. GitHub Secrets Setup

```
1. Go to: https://github.com/jayprophit/Financial-Master/settings/secrets/actions

2. Add Repository Secrets:
   - POLYGON_API_KEY
   - ALPACA_API_KEY
   - ALPACA_SECRET_KEY
   - ALPHA_VANTAGE_API_KEY
   - NEON_DATABASE_URL
   - JWT_SECRET_KEY
   - ENCRYPTION_KEY
   - RENDER_API_KEY (for deployment)
```

#### 3. Local Security

```powershell
# Create .env.local (never commit!)
# Add to .gitignore:
.env.local
.env.*.local
*.key
*.pem

# Set file permissions (Windows):
icacls .env /inheritance:r /grant:r "%username%:F"

# Encrypt sensitive files (optional):
# Use Windows BitLocker or VeraCrypt
```

---

## MONITORING & MAINTENANCE

### UptimeRobot Setup

```
1. Go to https://uptimerobot.com/dashboard
2. Add New Monitor:
   - Type: HTTP(s)
   - Friendly Name: Financial Master API
   - URL: https://financial-master-api.onrender.com/health
   - Monitoring Interval: 5 minutes
   - Alert Contact: Your email

3. Add Second Monitor:
   - Friendly Name: Financial Master Frontend
   - URL: https://financial-master-docs.pages.dev
```

### Sentry Error Tracking

```
1. Sign up: https://sentry.io/signup/
2. Create project: Python > FastAPI
3. Get DSN: Settings > Projects > Client Keys
4. Add to environment: SENTRY_DSN=your_dsn_here
```

### Daily Maintenance Checklist

| Task | Frequency | Command/Action |
|------|-----------|----------------|
| Check API status | Daily | curl /health endpoint |
| Review error logs | Daily | Sentry dashboard |
| Monitor disk space | Weekly | Check data/ folder size |
| Backup database | Weekly | Copy data/financial_master.db |
| Update dependencies | Monthly | pip list --outdated |
| Rotate API keys | Quarterly | Update all services |

---

## TROUBLESHOOTING

### Common Issues

#### Issue: Backend won't start

```powershell
# Check virtual environment
.venv\Scripts\Activate.ps1

# Verify dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
netstat -ano | findstr :8000

# Check logs
python -m src.backend.app.validate_setup
```

#### Issue: API keys not working

```powershell
# Verify .env file is loaded
Get-ChildItem .env

# Test individual API
curl "https://paper-api.alpaca.markets/v2/account" \
  -H "APCA-API-KEY-ID: $env:ALPACA_API_KEY" \
  -H "APCA-API-SECRET-KEY: $env:ALPACA_SECRET_KEY"
```

#### Issue: Database locked (SQLite)

```powershell
# Close all connections to the database
# Restart the application
# Or delete WAL files:
Remove-Item data/*.db-wal
Remove-Item data/*.db-shm
```

---

## UPGRADE PATHS

### When to Upgrade (Cost-Effective Triggers)

| Current Limit | Upgrade To | Cost | When |
|---------------|------------|------|------|
| Render sleeps (15min idle) | Render Starter | $7/mo | Daily active users |
| Neon 500MB full | Neon Pro | $19/mo | Database grows |
| API rate limits hit | Polygon Basic | $49/mo | Need real-time |
| Need 24/7 uptime | Railway/Render paid | $19/mo | Production use |
| Multiple users | Full VPS (Hetzner) | €5/mo | 5+ concurrent users |

### Production Architecture (Future)

```
┌────────────────────────────────────────────────────────────────┐
│                        PRODUCTION STACK                        │
│                                                                │
│  Frontend: Vercel Pro ($20/mo)                                 │
│  Backend: Railway Pro ($19/mo)                                 │
│  Database: Neon Pro ($19/mo)                                   │
│  Cache: Redis Cloud ($0 - free tier)                           │
│  Monitoring: Sentry Team ($26/mo)                              │
│  CDN: Cloudflare Pro ($20/mo)                                  │
│  Domain: Cloudflare Registrar ($8/yr)                          │
│                                                                │
│  Total: ~$104/month                                            │
└────────────────────────────────────────────────────────────────┘
```

---

## SUMMARY CHECKLIST

### Pre-Flight (Before First Run)

- [ ] GitHub account created
- [ ] Repository pushed to GitHub
- [ ] Cloudflare account ready
- [ ] Render account ready
- [ ] Neon account ready
- [ ] UptimeRobot account ready
- [ ] Alpaca paper trading API keys obtained
- [ ] Polygon.io API key obtained
- [ ] Alpha Vantage API key obtained
- [ ] Local Python environment set up
- [ ] .env file configured with all keys
- [ ] Dependencies installed
- [ ] Local database initialized
- [ ] Security keys generated

### Week 1 Goals

- [ ] Local backend running with mock data
- [ ] All unit tests passing
- [ ] Basic API endpoints tested
- [ ] Frontend connected to backend

### Week 2-4 Goals

- [ ] Switch to paper trading mode
- [ ] Execute 50+ paper trades
- [ ] Achieve 75%+ win rate
- [ ] Deploy to Render (backend)
- [ ] Deploy to Cloudflare Pages (docs)

### Week 5-8 Goals

- [ ] Backtesting with 2 years data
- [ ] Sharpe ratio > 1.5
- [ ] Max drawdown < 15%
- [ ] 90%+ success rate on signals
- [ ] Ready for small real money testing

### Success Metrics

| Milestone | Target Date | Success Criteria |
|-----------|-------------|------------------|
| MVP Local | Week 1 | All features working with mock data |
| Paper Trading | Week 4 | 75% win rate, 100+ trades |
| Live Testing | Week 8 | 90% accuracy, proven backtests |
| Production | Week 12 | Live trading with strict risk limits |

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-03  
**Next Review:** After first successful paper trading week

**Support Resources:**

- GitHub Issues: <https://github.com/jayprophit/Financial-Master/issues>
- Documentation: <https://financial-master-docs.pages.dev>
- API Status: <https://financial-master-api.onrender.com/health>
