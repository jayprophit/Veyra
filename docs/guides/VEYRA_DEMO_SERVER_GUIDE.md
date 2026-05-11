# 🌟 Veyra - Production Demo Server Guide

## Quick Start (GitHub Codespaces)

```bash
bash scripts/launch_demo.sh
```

The server will automatically detect Codespaces and provide you with your unique public URL.

## What is Veyra?

**Veyra** is an enterprise-grade autonomous wealth and finance platform featuring:

- ✅ **1025 Core Modules** - Complete financial stack
- ✅ **1063+ API Endpoints** - Full REST API coverage
- ✅ **18 Service Types** - Comprehensive service architecture
- ✅ **5 Integrations** - Third-party data connections
- ✅ **11 Capability Areas** - Full-stack coverage

### Key Capabilities

| Capability | Components | Status |
|-----------|-----------|--------|
| AI Intelligence | 141 | ✅ Ready |
| APIs | 151 | ✅ Ready |
| Automated Trading | 96 | ✅ Ready |
| Blockchain | 65 | ✅ Ready |
| Core Trading | 117 | ✅ Ready |
| Data Integration | 79 | ✅ Ready |
| Database | 64 | ✅ Ready |
| Mobile Support | 12 | ✅ Ready |
| Portfolio Management | 41 | ✅ Ready |
| Risk Analytics | 151 | ✅ Ready |
| Visualizations | 1 | ✅ Ready |

## Accessing Veyra

### Local Development
```bash
# Terminal 1: Start demo server
bash scripts/launch_demo.sh

# Terminal 2: Open in browser
open http://localhost:5000
```

### GitHub Codespaces
When running in Codespaces:
1. Run `bash scripts/launch_demo.sh`
2. Codespaces will detect port 5000
3. A notification will show your public URL
4. Click the notification or visit the URL in your browser

### API Documentation
Available at: `http://localhost:5000/docs`

## Demo Server Features

### Dashboard (`/`)
- Platform overview
- Statistics summary
- Quick links to main features

### Health Check (`/health`)
Shows system status:
```json
{
  "status": "✅ healthy",
  "service": "Veyra",
  "timestamp": "2026-05-11T05:00:10.123456",
  "version": "1.0.0"
}
```

### System Status (`/status`)
Platform metrics and operational status

### Performance Metrics (`/metrics`)
Real-time performance data

## Core API Endpoints

### Accounts
- `GET /api/v1/accounts` - List user accounts
- Response includes account balances and types

### Portfolio
- `GET /api/v1/portfolio` - Get portfolio holdings
- Shows positions, values, and performance

### Trading
- `POST /api/v1/trade` - Execute trade
- Get trade execution status

### AI Predictions
- `GET /api/v1/ai/predict?symbol=AAPL` - Market prediction
- Returns confidence and target price

### Analytics
- `GET /api/v1/analytics` - Financial analytics
- Shows performance metrics

## Architecture

### Project Structure
```
veyra/
├── src/backend/app/          # Core backend services
│   ├── api/                  # REST API endpoints
│   ├── ai/                   # AI/ML modules
│   ├── trading/              # Trading engine
│   ├── portfolio/            # Portfolio management
│   ├── risk/                 # Risk analytics
│   ├── blockchain/           # Blockchain integration
│   └── ...                   # 1000+ more modules
├── frontend/                 # React dashboard
├── mobile/veyra_app/         # Flutter mobile app
├── deploy/                   # Deployment configs
└── scripts/                  # Utility scripts
```

### Services (18 Types)
1. **AI/ML** - 110 modules
2. **APIs** - 90 modules
3. **Trading** - 70 modules
4. **Wealth Management** - 34 modules
5. **Analytics** - 27 modules
6. **Authentication** - 24 modules
7. **Risk Management** - 20 modules
8. **Portfolio** - 18 modules
9. **NLP** - 16 modules
10. **Monitoring** - 15 modules
11. **Blockchain** - 13 modules
12. **Database** - 12 modules
13. **DeFi** - 12 modules
14. **Compliance** - 8 modules
15. **Education** - 2 modules
16. **Treasury** - 2 modules
17. **Data Providers** - 1 module
18. **Institutional** - 1 module

## Configuration

### Environment Variables
```bash
# Port (default: 5000)
export PORT=5000

# Environment (development/staging/production)
export VEYRA_ENV=development
```

### External Services Setup

#### Cloudflare
1. Go to https://dash.cloudflare.com
2. Create a new account or login
3. Add your domain
4. Update DNS records
5. Deploy to Cloudflare Pages (optional)

#### Database (Optional)
1. Set up PostgreSQL/MySQL
2. Run migrations: `python3 scripts/setup/init_db.py`
3. Update connection string in `.env`

#### API Services (Optional)
Veyra uses free-tier APIs by default:
- Alpha Vantage (stocks)
- Binance (crypto)
- coingecko (crypto data)
- yfinance (market data)

## Testing

### Run Test Suite
```bash
pytest tests/

# With coverage
pytest tests/ --cov

# Specific test
pytest tests/unit/test_api.py -v
```

### Run Comprehensive Tests
```bash
python3 scripts/tools/audit/run_production_tests.py
```

## Development

### Code Quality Check
```bash
# Format code
black src/ --line-length=120

# Lint
flake8 src/ --max-line-length=120

# Type checking
mypy src/
```

### Run with Hot Reload
```bash
# Install watchdog
pip install watchdog

# Start with auto-reload
PYTHONUNBUFFERED=1 python3 -m uvicorn \
  src.backend.app.veyra_demo_server:app \
  --reload --host 0.0.0.0 --port 5000
```

## Production Deployment

### Using Docker
```bash
docker build -t veyra:latest .
docker run -p 5000:5000 veyra:latest
```

### Using Render (Free Tier)
1. Push to GitHub
2. Connect repository to Render
3. Deploy: `bash scripts/deployment/deploy_zero_cost.py`

### Using Cloudflare Pages + Workers
1. `npm run build` in frontend/
2. Deploy to Cloudflare Pages
3. Backend on Workers (Python not supported - use Node proxy)

## Monitoring & Logs

### View Logs
```bash
# Application logs
tail -f data/logs/*.log

# Real-time monitoring
python3 scripts/tools/audit/run_production_tests.py
```

### Performance Monitoring
Access `/metrics` endpoint for real-time metrics

## Troubleshooting

### Port Already in Use
```bash
# Use different port
PORT=8000 bash scripts/launch_demo.sh

# Kill existing process
lsof -ti:5000 | xargs kill -9
```

### ImportError
```bash
# Reinstall dependencies
pip install -r requirements.txt -r requirements_ai.txt -r requirements_opensource.txt
```

### Virtual Environment Issues
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Support & Documentation

- **Full Docs**: See `/docs` directory
- **Architecture**: See `docs/architecture/`
- **API Reference**: Visit `http://localhost:5000/docs`
- **Examples**: See `examples/` directory

## Next Steps

1. ✅ Start demo server: `bash scripts/launch_demo.sh`
2. ✅ Open dashboard: http://localhost:5000
3. ✅ Explore API docs: http://localhost:5000/docs
4. ✅ Configure external services (Cloudflare, etc.)
5. ✅ Deploy to production

---

**Version**: 1.0.0  
**Last Updated**: 2026-05-11  
**Status**: 🚀 Production Ready
