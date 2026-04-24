# Automation Layer - Quick Guide

## Files Created
- `20_Automation_Controller.py` - Master automation controller
- `AUTO_SETUP.ps1` - One-click PowerShell setup
- `21_Data_Scraper.py` - Broker/CSV importers
- `22_Build_Automation.py` - Automated builds

## Usage

### 1. One-Click Setup
```powershell
.\AUTO_SETUP.ps1 -FullSetup
```

### 2. Python Automation
```python
from automation_controller import MasterAutomationController

c = MasterAutomationController()
c.auto_setup()              # Setup everything
c.setup_ollama()            # Download LLM models
c.setup_docker()            # Start containers
c.open_dashboard()          # Open browser
```

### 3. Desktop Automation
```python
from automation_controller import DesktopAutomation

d = DesktopAutomation()
d.screenshot()               # Capture screen
d.open_app("notepad")        # Open application
d.open_browser("http://localhost:5173")
```

### 4. Data Import
```python
from data_scraper import Trading212Importer, YahooFinanceScraper

t212 = Trading212Importer()
transactions = t212.parse("export.csv")

yahoo = YahooFinanceScraper()
price = yahoo.get_info("AAPL")
```

### 5. Build Automation
```python
from build_automation import BuildAutomator

b = BuildAutomator()
b.full_build()               # Build dashboard + Docker
```

## Ollama Models Available
Run `.\AUTO_SETUP.ps1 -OllamaOnly` to download:
- llama3.2:3b (2GB) - Fast summaries
- llama3.1:8b (4.7GB) - Analysis
- qwen2.5:7b (4.4GB) - JSON/structured
- phi4 (9.1GB) - Math/reasoning
- nomic-embed-text (274MB) - Embeddings

## Windows Integration
- PowerShell automation: winget, scheduled tasks
- WSL integration: Linux tools, Docker
- Desktop: pyautogui, browser control
- System: health monitoring, auto-restart
