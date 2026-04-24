# Complete Automation Guide

## New Automation Files (Files 27-30)

| File | Purpose | Integration |
|------|---------|-------------|
| `27_Git_Automation.py` | Git/GitHub Desktop | Version control, CI/CD |
| `28_WSL2_Ubuntu.py` | WSL2/Ubuntu | Linux tools, Docker in WSL |
| `29_MSYS2_Integration.py` | MSYS2/MinGW | C/C++ compilation |
| `30_Autonomous_Browser.py` | AI Web Automation | Pagination, scraping |

## Total System: 38+ Files

## 1. Git Automation (27_Git_Automation.py)

### Features
- Git operations: init, add, commit, push, pull
- GitHub Desktop integration
- Automatic commit messages
- Branch management
- CI/CD workflow creation

### Usage
```python
from git_automation import GitManager, GitHubManager

# Basic git
git = GitManager('.')
git.init_repo()
git.add()
git.commit("Initial commit")
git.push()

# GitHub
gh = GitHubManager(token='your_token')
gh.create_repo('financial-master', private=True)
gh.sync_to_github('.')
```

## 2. WSL2/Ubuntu Integration (28_WSL2_Ubuntu.py)

### Features
- WSL distribution management
- Package installation
- Docker in WSL (native)
- Port forwarding
- Systemd services
- Swap file creation

### Usage
```python
from wsl2_ubuntu import WSL2Manager, UbuntuAutomation

# WSL2
wsl = WSL2Manager('Ubuntu')
wsl.setup_development_environment()
wsl.setup_docker_in_wsl()
wsl.install_packages(['nodejs', 'npm', 'postgresql'])

# Ubuntu-specific
ubuntu = UbuntuAutomation(wsl)
ubuntu.setup_nodejs(20)
ubuntu.setup_postgres()
ubuntu.optimize_for_ollama()  # 8GB swap
ubuntu.create_systemd_service('financial-master', 'python main.py')
```

## 3. MSYS2 Integration (29_MSYS2_Integration.py)

### Features
- MinGW64 toolchain
- C/C++ compilation
- pacman package management
- Python/Node in MSYS2
- PATH management

### Usage
```python
from msys2_integration import MSYS2Manager, MinGWCompiler

# MSYS2
msys = MSYS2Manager()
msys.setup_development_tools()
msys.install_package('mingw-w64-x86_64-python')
msys.update_system()
msys.add_to_path()

# C/C++ compilation
compiler = MinGWCompiler(msys)
compiler.compile_c('main.c', 'app.exe')
compiler.compile_cpp('app.cpp', 'app.exe', ['-O3', '-std=c++17'])
```

## 4. Autonomous Browser (30_Autonomous_Browser.py)

### Features
- **AI-driven navigation**
- **Multi-page pagination** (scroll, click next)
- **Form automation**
- **Screenshot documentation**
- **Anti-detection (stealth mode)**
- **Rate limiting**

### Usage
```python
import asyncio
from autonomous_browser import AutonomousBrowser, ScrapingTask

async def main():
    browser = AutonomousBrowser(headless=False)
    await browser.init()
    
    # Define scraping task with pagination
    task = ScrapingTask(
        url='https://finance.yahoo.com/quote/AAPL/news',
        goal='Extract financial news',
        selectors={
            'headlines': 'h3',
            'summaries': 'p',
            'dates': 'time'
        },
        max_pages=5,           # Scrape 5 pages
        scroll_to_bottom=True, # Auto-scroll
        wait_for='h3'          # Wait for content
    )
    
    # Scrape with pagination
    result = await browser.scrape_with_pagination(task)
    
    print(f"Scraped {result.pages_scraped} pages")
    print(f"Data: {len(result.data)} items")
    print(f"Screenshots: {result.screenshots}")
    
    await browser.close()

asyncio.run(main())
```

### Built-in Scrapers
```python
# Financial news
result = await browser.scrape_financial_news(
    source='yahoo',
    ticker='AAPL',
    max_pages=3
)

# Autonomous search
results = await browser.autonomous_search_and_scrape(
    query='financial master portfolio management',
    llm_guidance=True
)
```

## Integration Matrix

| Tool | Works With | Best For |
|------|-----------|----------|
| **WSL2** | Docker, Linux tools | Development environment |
| **MSYS2** | MinGW, C/C++ | Native Windows compilation |
| **Git** | GitHub, CI/CD | Version control |
| **Autonomous Browser** | Playwright, AI | Web scraping, pagination |

## Complete Workflow Example

```python
from automation_controller import MasterAutomationController
from git_automation import GitManager
from wsl2_ubuntu import WSL2Manager, UbuntuAutomation
from autonomous_browser import AutonomousBrowser
import asyncio

class FullAutomation:
    def __init__(self):
        self.controller = MasterAutomationController()
        self.git = GitManager('.')
        self.wsl = WSL2Manager()
        self.ubuntu = UbuntuAutomation(self.wsl)
    
    def setup_environment(self):
        """Setup complete dev environment."""
        # WSL2
        self.wsl.setup_development_environment()
        self.wsl.setup_docker_in_wsl()
        self.ubuntu.optimize_for_ollama()
        
        # Git
        if not self.git.is_repo():
            self.git.init_repo()
        
        # Ollama
        self.controller.setup_ollama()
    
    async def scrape_market_data(self):
        """Autonomous market data scraping."""
        browser = AutonomousBrowser()
        await browser.init()
        
        # Scrape multiple sources
        sources = ['yahoo', 'bloomberg', 'ft']
        results = []
        
        for source in sources:
            result = await browser.scrape_financial_news(source, max_pages=2)
            results.append(result)
        
        await browser.close()
        return results
    
    def commit_and_push(self, message="Automated update"):
        """Git workflow."""
        self.git.auto_commit_all(message)
        self.git.push()
    
    def run_full_pipeline(self):
        """Execute full automation pipeline."""
        # 1. Setup
        self.setup_environment()
        
        # 2. Scrape data
        asyncio.run(self.scrape_market_data())
        
        # 3. Commit
        self.commit_and_push("Market data update")
        
        # 4. Deploy (WSL)
        self.wsl.run_command("docker-compose up -d")

# Usage
if __name__ == "__main__":
    auto = FullAutomation()
    auto.run_full_pipeline()
```

## Prerequisites

```powershell
# Install all dependencies
pip install pyautogui uiautomation selenium playwright docker kubernetes psutil pystray pdfplumber yfinance pillow requests pygithub

# Playwright browsers
playwright install

# Optional: WSL2 (if not installed)
wsl --install -d Ubuntu

# Optional: MSYS2 (if not installed)
# Download from https://www.msys2.org/
```

## Quick Commands

```powershell
# Git operations
python -c "from git_automation import GitManager; g = GitManager('.'); g.auto_commit_all(); g.push()"

# WSL setup
python -c "from wsl2_ubuntu import WSL2Manager; w = WSL2Manager(); w.setup_development_environment(); w.setup_docker_in_wsl()"

# MSYS2 setup
python -c "from msys2_integration import MSYS2Manager; m = MSYS2Manager(); m.setup_development_tools()"

# Browser scraping
python -c "import asyncio; from autonomous_browser import AutonomousBrowser, ScrapingTask; async def x(): b = AutonomousBrowser(); await b.init(); r = await b.scrape_financial_news('yahoo', 'AAPL', 2); print(r.data); await b.close(); asyncio.run(x())"
```

## File Count Summary

| Category | Count |
|----------|-------|
| Core Python (06-19) | 14 |
| Automation (20-30) | 11 |
| PowerShell/Batch | 4 |
| Dashboard | 15 |
| Docker/Config | 5 |
| Documentation | 5 |
| **Total** | **54+ files** |

## Next Steps

1. Install prerequisites
2. Run `AUTO_SETUP.ps1 -FullSetup`
3. Start system: `QUICKSTART.bat`
4. Use automation:
   - Git: `python 27_Git_Automation.py`
   - WSL: `python 28_WSL2_Ubuntu.py`
   - MSYS2: `python 29_MSYS2_Integration.py`
   - Browser: `python 30_Autonomous_Browser.py`
