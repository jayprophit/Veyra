# Financial Master - 5-Star Portfolio Management System

A comprehensive, AI-powered portfolio management system with zero operating costs (free tier using Ollama, SQLite) and optional paid upgrades for scale.

## Quick Start

```bash
# 1. Setup (installs Python deps, creates directories)
.\COMPLETE_SETUP.bat

# 2. Configure
copy .env.example .env
# Edit .env with your settings (optional for free tier)

# 3. Start everything
python main.py

# 4. Or start components individually
python 19_API_Server.py          # REST API on http://localhost:8000
python 15_WebSocket_Real_Time_Feeds.py  # WebSocket on ws://localhost:8765

# 5. Start dashboard
cd dashboard
npm install
npm run dev                      # http://localhost:5173
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REACT DASHBOARD                           │
│         (Real-time portfolio, agents, tax, retirement)        │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Server (19_API_Server.py)                          │
│  ├─ /api/portfolio/summary                                  │
│  ├─ /api/agents/status                                      │
│  ├─ /api/tax/harvest-opportunities                          │
│  └─ /api/retirement/monte-carlo                             │
├─────────────────────────────────────────────────────────────┤
│  8 AI AGENTS (14_Autonomous_Agent_Framework.py)             │
│  ├─ Market Data Collector                                   │
│  ├─ Tax Optimizer (CGT, ISA, Tax-Loss Harvesting)          │
│  ├─ Risk Manager                                            │
│  ├─ Portfolio Rebalancer                                    │
│  ├─ Retirement/FIRE Planner                                 │
│  ├─ Withdrawal Strategist                                   │
│  ├─ Sentiment Analyzer                                      │
│  └─ Compliance Auditor                                      │
├─────────────────────────────────────────────────────────────┤
│  LLM: Ollama (local) / OpenAI (optional)                   │
│  13_LLM_Integration_Free_Tier.py                            │
│  - llama3.2:3b (fast summaries)                           │
│  - llama3.1:8b (analysis)                                   │
│  - qwen2.5:7b (structured data)                           │
├─────────────────────────────────────────────────────────────┤
│  DATABASE: SQLite (local) / PostgreSQL (scalable)        │
│  16_Database_Layer.py                                       │
│  ├─ Holdings                                              │
│  ├─ Transactions                                          │
│  ├─ Tax Records                                           │
│  └─ Agent Decisions                                       │
├─────────────────────────────────────────────────────────────┤
│  DATA FEEDS: Mock (free) / Finnhub (free tier)              │
│  15_WebSocket_Real_Time_Feeds.py                          │
│  WebSocket broadcasts to dashboard                          │
└─────────────────────────────────────────────────────────────┘
```

## Cost Breakdown

| Component | Free Tier | Paid Tier |
|-----------|-----------|-----------|
| **LLM** | Ollama (local): £0 | GPT-4o-mini: £5-15/mo |
| **Database** | SQLite: £0 | PostgreSQL: £10-50/mo |
| **Data Feeds** | Mock/Finnhub free: £0 | Polygon pro: £50-200/mo |
| **Hosting** | Local/self-hosted: £0 | VPS/Cloud: £10-100/mo |
| **Total** | **£0/month** | **£75-365/month** |

## Key Features

### 1. Tax-Loss Harvesting (17_Tax_Loss_Harvesting.py)
- Automatic detection of unrealized losses
- 30-day wash sale rule compliance (UK)
- Bed & ISA optimization
- CGT allowance tracking (£3,000/year)
- Fund replacement suggestions

### 2. Retirement Planning (18_Retirement_Monte_Carlo.py)
- Monte Carlo simulation (10,000+ iterations)
- FIRE number calculation
- Safe withdrawal rate analysis
- Multiple withdrawal strategies comparison
- Years-to-FIRE projection

### 3. AI Agents with Guardrails (14_Autonomous_Agent_Framework.py)
- Human approval gates for high-value trades
- Kill switch for emergency stop
- Daily limits and circuit breakers
- Full audit trail in SQLite

### 4. Real-Time Data (15_WebSocket_Real_Time_Feeds.py)
- WebSocket server for live prices
- Mock mode (no API key needed)
- Finnhub integration (free tier)
- Automatic reconnection

## File Overview

| File | Purpose |
|------|---------|
| `main.py` | System orchestrator - start everything |
| `19_API_Server.py` | FastAPI REST backend |
| `13_LLM_Integration_Free_Tier.py` | Ollama + paid fallback |
| `14_Autonomous_Agent_Framework.py` | Multi-agent system with guardrails |
| `15_WebSocket_Real_Time_Feeds.py` | Real-time price feeds |
| `16_Database_Layer.py` | SQLite/PostgreSQL interface |
| `17_Tax_Loss_Harvesting.py` | CGT optimization |
| `18_Retirement_Monte_Carlo.py` | Retirement simulation |
| `12_Telegram_Bot.py` | Mobile command center |
| `dashboard/` | React + TypeScript frontend |

## Docker Deployment

```bash
# Start everything with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down

# Backup
docker-compose exec backup backup
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/portfolio/summary` | Portfolio overview |
| `GET /api/holdings` | All holdings |
| `GET /api/tax/harvest-opportunities` | Tax-loss opportunities |
| `POST /api/retirement/monte-carlo` | Run simulation |
| `GET /api/agents/status` | Agent status |
| `POST /api/agents/decisions/{id}/approve` | Approve action |

See full docs at `http://localhost:8000/docs` when API is running.

## Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Required for free tier (all have defaults)
DB_TYPE=sqlite
OLLAMA_MODEL=llama3.2:3b
USE_MOCK_DATA=true

# Optional (for paid features)
OPENAI_API_KEY=sk-...
FINNHUB_API_KEY=...
TELEGRAM_BOT_TOKEN=...
```

## Security & Safety

- **Kill Switch**: `POST /api/system/kill-switch` stops all agents
- **Approval Gates**: Trades >£10k require human approval
- **Daily Limits**: Max 5 trades, £100k value, £5k loss
- **Audit Trail**: All decisions logged to SQLite
- **100% Local**: With free tier, no data leaves your machine

## Testing

```bash
# Run API health check
curl http://localhost:8000/api/health

# Test Monte Carlo simulation
curl -X POST http://localhost:8000/api/retirement/monte-carlo \
  -H "Content-Type: application/json" \
  -d '{"current_age":35,"retirement_age":60,"current_savings":200000,"monthly_contribution":1500,"annual_withdrawal":45000}'

# View tax opportunities
curl http://localhost:8000/api/tax/harvest-opportunities
```

## Telegram Bot Commands

Once configured with `TELEGRAM_BOT_TOKEN`:
- `/status` - System status
- `/agents` - Agent status
- `/alerts` - Pending decisions
- `/approve {id}` - Approve decision
- `/kill` - Emergency stop
- `/cgt` - CGT summary
- `/isa` - ISA status

## License

MIT - You own your IP. All components are open source.

## Support

- API Docs: http://localhost:8000/docs
- Source: `07_Working_Files/00_Master_Spreadsheet_System/`
- Setup: Run `COMPLETE_SETUP.bat`
