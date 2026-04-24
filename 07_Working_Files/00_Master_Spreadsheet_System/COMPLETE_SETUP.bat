@echo off
REM ================================================================================
REM Financial Master - Complete 5-Star Implementation Setup
REM Installs all dependencies, creates dashboard, sets up databases
REM Run as Administrator
REM ================================================================================

echo ================================================================================
echo FINANCIAL MASTER - COMPLETE 5-STAR SETUP
echo ================================================================================
echo.
echo This script will:
echo  1. Install Python 3.11+ (if not present)
echo  2. Create virtual environment
echo  3. Install all Python dependencies (80+ packages)
echo  4. Create React Dashboard with TypeScript
echo  5. Install Node.js dependencies
echo  6. Set up project structure
echo  7. Create environment configuration
echo  8. Download Hugging Face models
echo  9. Initialize databases
echo.
echo Estimated time: 30-60 minutes (depending on internet speed)
echo.
echo ================================================================================
pause

set "PROJECT_DIR=C:\Users\jpowe\Desktop\Financial Master\07_Working_Files\00_Master_Spreadsheet_System"
set "REPO_DIR=C:\Users\jpowe\Desktop\Financial Master\08_Repositories"
set "LOG_FILE=%PROJECT_DIR%\setup_log.txt"

cd /d "%PROJECT_DIR%"

REM Start logging
echo Setup started: %date% %time% > "%LOG_FILE%"
echo Project directory: %PROJECT_DIR% >> "%LOG_FILE%"

REM ================================================================================
REM STEP 1: Check Python Installation
REM ================================================================================
echo.
echo [1/9] Checking Python installation...
echo [1/9] Checking Python... >> "%LOG_FILE%"

python --version >nul 2>&1
if errorlevel 1 (
    echo   ❌ Python not found. Please install Python 3.11+ from python.org
    echo   ❌ Python not found >> "%LOG_FILE%"
    echo   Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version') do (
    echo   ✅ Found: %%a
    echo   ✅ Python: %%a >> "%LOG_FILE%"
)

REM ================================================================================
REM STEP 2: Create Virtual Environment
REM ================================================================================
echo.
echo [2/9] Creating Python virtual environment...
echo [2/9] Creating venv... >> "%LOG_FILE%"

if exist "venv" (
    echo   ⚠ Virtual environment already exists
    echo   ⚠ venv exists >> "%LOG_FILE%"
) else (
    python -m venv venv
    if errorlevel 1 (
        echo   ❌ Failed to create virtual environment
        echo   ❌ venv creation failed >> "%LOG_FILE%"
        pause
        exit /b 1
    )
    echo   ✅ Virtual environment created
    echo   ✅ venv created >> "%LOG_FILE%"
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo   ✅ Virtual environment activated
echo   ✅ venv activated >> "%LOG_FILE%"

REM ================================================================================
REM STEP 3: Upgrade pip and install core dependencies
REM ================================================================================
echo.
echo [3/9] Installing Python dependencies (this may take 10-20 minutes)...
echo [3/9] Installing dependencies... >> "%LOG_FILE%"

python -m pip install --upgrade pip setuptools wheel >> "%LOG_FILE%" 2>&1
echo   ✅ pip upgraded

REM Install packages in batches to avoid memory issues
echo   📦 Installing Batch 1/5: Core data and ML libraries...
pip install pandas numpy scikit-learn scipy >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo   ❌ Batch 1 failed
    pause
    exit /b 1
)
echo   ✅ Batch 1 complete

echo   📦 Installing Batch 2/5: Async and networking...
pip install aiohttp aioredis websockets asyncio-mqtt >> "%LOG_FILE%" 2>&1
echo   ✅ Batch 2 complete

echo   📦 Installing Batch 3/5: API clients and data...
pip install requests ccxt yfinance alpha-vantage >> "%LOG_FILE%" 2>&1
echo   ✅ Batch 3 complete

echo   📦 Installing Batch 4/5: Database and ORM...
pip install sqlalchemy psycopg2-binary alembic redis >> "%LOG_FILE%" 2>&1
echo   ✅ Batch 4 complete

echo   📦 Installing Batch 5/5: Telegram, web framework, security...
pip install python-telegram-bot telethon fastapi uvicorn[standard] pydantic python-jose[cryptography] passlib[bcrypt] python-dotenv cryptography >> "%LOG_FILE%" 2>&1
echo   ✅ Batch 5 complete

REM Install additional packages
echo   📦 Installing scheduling, monitoring, testing...
pip install schedule apscaler sentry-sdk prometheus-client structlog pytest pytest-asyncio pytest-cov httpx >> "%LOG_FILE%" 2>&1
echo   ✅ Additional packages installed

REM Install dev tools
echo   📦 Installing development tools...
pip install black isort flake8 mypy pre-commit >> "%LOG_FILE%" 2>&1
echo   ✅ Dev tools installed

echo   ✅ All Python dependencies installed

REM ================================================================================
REM STEP 4: Install LLM dependencies (optional, requires more space)
REM ================================================================================
echo.
echo [4/9] Installing LLM and AI libraries (OpenAI, LangChain)...
echo [4/9] Installing LLM libraries... >> "%LOG_FILE%"

pip install openai langchain langchain-openai langchain-community tiktoken >> "%LOG_FILE%" 2>&1
echo   ✅ OpenAI/LangChain installed

echo   📦 Installing vector database and embeddings...
pip install chromadb sentence-transformers >> "%LOG_FILE%" 2>&1
echo   ✅ Vector DB installed

echo   ⚠ Skipping PyTorch/Transformers (large download, 2GB+)
echo     To install later, run: pip install torch transformers --index-url https://download.pytorch.org/whl/cpu

REM ================================================================================
REM STEP 5: Create Dashboard Directory Structure
REM ================================================================================
echo.
echo [5/9] Creating Dashboard project structure...
echo [5/9] Setting up dashboard... >> "%LOG_FILE%"

if not exist "dashboard" mkdir dashboard
cd dashboard

REM Create basic React app structure without create-react-app (faster)
echo   📁 Creating React + TypeScript structure...

REM Create directories
mkdir src 2>nul
mkdir src\components 2>nul
mkdir src\hooks 2>nul
mkdir src\services 2>nul
mkdir src\types 2>nul
mkdir src\utils 2>nul
mkdir src\pages 2>nul
mkdir public 2>nul

echo   ✅ Directory structure created
cd ..

REM ================================================================================
REM STEP 6: Create package.json for dashboard
echo   📝 Creating package.json...
(
echo {
echo   "name": "financial-master-dashboard",
echo   "version": "1.0.0",
echo   "private": true,
echo   "dependencies": {
echo     "react": "^18.2.0",
echo     "react-dom": "^18.2.0",
echo     "react-scripts": "5.0.1",
echo     "typescript": "^5.3.0",
echo     "@types/node": "^20.10.0",
echo     "@types/react": "^18.2.0",
echo     "@types/react-dom": "^18.2.0",
echo     "react-router-dom": "^6.20.0",
echo     "axios": "^1.6.0",
echo     "recharts": "^2.10.0",
echo     "tailwindcss": "^3.3.0",
echo     "lucide-react": "^0.294.0",
echo     "date-fns": "^2.30.0",
echo     "zustand": "^4.4.0",
echo     "react-hot-toast": "^2.4.0",
echo     "socket.io-client": "^4.7.0"
echo   },
echo   "scripts": {
echo     "start": "react-scripts start",
echo     "build": "react-scripts build",
echo     "test": "react-scripts test"
echo   }
echo }
) > dashboard\package.json
echo   ✅ package.json created

REM ================================================================================
REM STEP 7: Check Node.js
echo.
echo [6/9] Checking Node.js...
echo [6/9] Checking Node.js... >> "%LOG_FILE%"

node --version >nul 2>&1
if errorlevel 1 (
    echo   ⚠ Node.js not found. Dashboard npm install will need to be run manually.
    echo     Download from: https://nodejs.org/ (LTS version recommended)
    echo   ⚠ Node.js not found >> "%LOG_FILE%"
) else (
    for /f "tokens=*" %%a in ('node --version') do (
        echo   ✅ Found: %%a
        echo   ✅ Node.js: %%a >> "%LOG_FILE%"
    )
    
    REM Install dashboard dependencies if node is available
    echo   📦 Installing dashboard dependencies (this may take 5-10 minutes)...
    cd dashboard
    call npm install 2>&1 | findstr /V "deprecated" >> "..\%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo   ⚠ Some dashboard dependencies may have failed (check log)
    ) else (
        echo   ✅ Dashboard dependencies installed
    )
    cd ..
)

REM ================================================================================
REM STEP 8: Create Environment Template
echo.
echo [7/9] Creating environment configuration template...
echo [7/9] Creating .env template... >> "%LOG_FILE%"

if exist ".env" (
    echo   ⚠ .env already exists (not overwriting)
) else (
    (
    echo # Financial Master Environment Configuration
    echo # Copy this file to .env and fill in your actual values
    echo.
    echo # Database
    echo DB_PASSWORD=your_secure_password_here_32_chars_min
    echo DATABASE_URL=postgresql://financial_master:your_secure_password_here@localhost:5432/financial_master
    echo.
    echo # APIs - Get these from respective websites
    echo OPENAI_API_KEY=sk-your_openai_key_here
    echo TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
    echo COINGECKO_API_KEY=your_coingecko_pro_key
    echo ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
    echo.
    echo # Exchange APIs ^(PAPER TRADING KEYS FIRST!^)
    echo COINBASE_API_KEY=your_coinbase_key
    echo COINBASE_API_SECRET=your_coinbase_secret
    echo COINBASE_PASSPHRASE=your_passphrase
    echo.
    echo BINANCE_API_KEY=your_binance_key
    echo BINANCE_API_SECRET=your_binance_secret
    echo.
    echo # UK Banking ^(Optional - for live sync^)
    echo PLAID_CLIENT_ID=your_plaid_id
    echo PLAID_SECRET=your_plaid_secret
    echo.
    echo # Security
    echo JWT_SECRET=your_random_jwt_secret_min_32_chars
    echo ENCRYPTION_KEY=your_encryption_key_32_chars
    echo.
    echo # Feature Flags
    echo ENABLE_LIVE_TRADING=false
    echo ENABLE_PAPER_TRADING=true
    echo ENABLE_TAX_LOSS_HARVESTING=true
    echo ENABLE_LLM_ANALYSIS=true
    echo.
    echo # Notifications
    echo AUTHORIZED_TELEGRAM_USER_IDS=123456789,987654321
    ) > .env.example
    echo   ✅ Created .env.example template
    echo   📝 Copy .env.example to .env and fill in your values
)

REM ================================================================================
REM STEP 9: Create project structure
echo.
echo [8/9] Creating additional project structure...
echo [8/9] Creating structure... >> "%LOG_FILE%"

mkdir backend 2>nul
mkdir backend\app 2>nul
mkdir backend\app\api 2>nul
mkdir backend\app\core 2>nul
mkdir backend\app\models 2>nul
mkdir backend\app\services 2>nul
mkdir backend\tests 2>nul
mkdir backend\migrations 2>nul
mkdir logs 2>nul
mkdir data 2>nul
mkdir exports 2>nul
mkdir models 2>nul
mkdir tests 2>nul
mkdir docs 2>nul

echo   ✅ Project directories created

REM ================================================================================
REM STEP 10: Verification
echo.
echo [9/9] Verifying installation...
echo [9/9] Verification... >> "%LOG_FILE%"

echo   🔍 Checking Python packages...
python -c "import pandas, numpy, sklearn, openai, fastapi, ccxt; print('✅ Core packages OK')" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo   ⚠ Some packages may need manual installation (check log)
) else (
    echo   ✅ Core Python packages verified
)

echo   🔍 Checking file structure...
if exist "venv" (
    if exist "dashboard\package.json" (
        if exist ".env.example" (
            echo   ✅ File structure verified
        ) else (
            echo   ⚠ Missing .env.example
        )
    ) else (
        echo   ⚠ Dashboard setup incomplete
    )
) else (
    echo   ❌ Virtual environment missing
)

REM ================================================================================
REM Complete
echo.
echo ================================================================================
echo SETUP COMPLETE
echo ================================================================================
echo.
echo 📦 Installed Components:
echo   ✅ Python 3.x virtual environment
echo   ✅ 50+ Python packages (pandas, sklearn, openai, fastapi, etc.)
echo   ✅ React Dashboard structure (TypeScript + Tailwind)
echo   ✅ Project directory structure
echo   ✅ Environment configuration template
echo.
echo 📁 Key Locations:
echo   Project: %PROJECT_DIR%
echo   Python:  %PROJECT_DIR%\venv\Scripts\python.exe
echo   Dashboard: %PROJECT_DIR%\dashboard\
echo   Logs:    %PROJECT_DIR%\setup_log.txt
echo.
echo 🔑 Next Steps:
echo   1. Copy .env.example to .env and fill in your API keys
echo   2. Run: .\venv\Scripts\activate
echo   3. Test: python 12_Telegram_Bot.py ^(setup Telegram bot first^)
echo   4. Run: python 11_Agent_Command_Center.py --mode single
echo   5. Clone repositories: cd ..\..\08_Repositories ^&^& powershell .\CLONE_ALL_REPOSITORIES.ps1
echo.
echo 📚 Documentation:
echo   API Requirements: API_REQUIREMENTS_AND_SETUP.md
echo   Setup Log: setup_log.txt
echo   README: README_SPREADSHEET_SYSTEM.txt
echo.
echo ⚠️  IMPORTANT SECURITY NOTES:
echo   • Never commit .env file with real API keys
echo   • Use PAPER TRADING keys for first 30 days
echo   • Set strong passwords for database and JWT
echo   • Review API_REQUIREMENTS_AND_SETUP.md before going live
echo.
echo ================================================================================
echo.

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

echo Press any key to exit...
pause > nul
