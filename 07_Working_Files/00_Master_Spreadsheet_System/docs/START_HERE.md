# START HERE - Financial Master 5-Star System

## 🚀 First Time Setup (5 minutes)

### Step 1: Validate Your System
```powershell
python VALIDATE_SETUP.py
```
This checks all prerequisites and tells you what's missing.

### Step 2: One-Click Setup
```powershell
.\AUTO_SETUP.ps1 -FullSetup
```
This installs Ollama models, Python packages, Node dependencies, and starts everything.

### Step 3: Launch System
```powershell
.\QUICKSTART.bat
```

### Step 4: Access Dashboard
Open browser to: **http://localhost:5173**

---

## 📁 File Reference

### Must Know Files
| File | What It Does | When To Use |
|------|--------------|-------------|
| `VALIDATE_SETUP.py` | Checks prerequisites | First run, troubleshooting |
| `AUTO_SETUP.ps1` | One-click full setup | New installation |
| `QUICKSTART.bat` | Quick launch | Daily use |
| `main.py` | System orchestrator | Custom startup |
| `19_API_Server.py` | REST API | Backend development |

### Core Features (06-19)
- **13**: LLM (Ollama + paid fallback)
- **14**: 8 AI Agents with guardrails
- **15**: Real-time WebSocket
- **16**: Database (SQLite/PostgreSQL)
- **17**: Tax-loss harvesting
- **18**: Retirement Monte Carlo
- **19**: FastAPI server

### Automation Layer (20-31)
- **20**: Master automation controller
- **25**: Windows system tray app
- **27**: Git/GitHub integration
- **28**: WSL2/Ubuntu
- **29**: MSYS2/MinGW
- **30**: Autonomous browser (pagination!)
- **31**: Financial data scraper

---

## 💡 Common Tasks

### Start Everything
```powershell
.\QUICKSTART.bat
```

### Start Only API
```powershell
python 19_API_Server.py
```

### Import Trading 212 Data
```python
from data_scraper import Trading212Importer
importer = Trading212Importer()
data = importer.parse("export.csv")
```

### Scrape Yahoo Finance with Pagination
```python
import asyncio
from financial_scraper import YahooFinanceScraper

async def scrape():
    scraper = YahooFinanceScraper()
    await scraper.init()
    news = await scraper.get_news("AAPL", pages=5)  # 5 pages!
    print(f"Scraped {news.pages_scraped} pages")
    await scraper.close()

asyncio.run(scrape())
```

### Run Tests
```powershell
python 26_Integration_Tests.py
```

### Update Everything
```powershell
.\AUTO_SETUP.ps1 -FullSetup
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | Change in .env: `API_PORT=8001` |
| Ollama not found | Run: `pip install ollama` or check if installed |
| Node modules missing | `cd dashboard && npm install` |
| Python packages missing | `pip install -r requirements.txt` |
| WSL not working | `wsl --install -d Ubuntu` |

---

## 📊 System Status

Check status at: **http://localhost:8000/api/system/status**

Expected output:
```json
{
  "api_running": true,
  "database_connected": true,
  "websocket_status": "connected",
  "agents_running": 8,
  "pending_decisions": 0
}
```

---

## 🎯 What's Included

✅ **38 Python files** (10,000+ lines)
✅ **15 Dashboard files** (React + TypeScript)
✅ **Git automation**
✅ **WSL2/Ubuntu integration**
✅ **MSYS2/MinGW compilation**
✅ **Autonomous browser with pagination**
✅ **Windows system tray app**
✅ **Docker/Kubernetes support**
✅ **8 AI agents**
✅ **Tax-loss harvesting**
✅ **Monte Carlo retirement**

---

## 📞 Support

- **API Docs**: http://localhost:8000/docs (when running)
- **Validate**: `python VALIDATE_SETUP.py`
- **Quick Start**: `.\QUICKSTART.bat`

## ⚡ Quick Command Reference

```powershell
# Validate setup
python VALIDATE_SETUP.py

# Full setup
.\AUTO_SETUP.ps1 -FullSetup

# Quick start
.\QUICKSTART.bat

# Test
python 26_Integration_Tests.py

# System tray
python 25_System_Tray.py

# Scrape data
python 31_Financial_Scraper.py
```

**You're ready to go! Start with:** `.\QUICKSTART.bat`
