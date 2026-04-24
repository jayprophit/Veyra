@echo off
echo ================================================
echo Financial Master - Quick Start
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    exit /b 1
)

REM Check Node
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js 20+
    exit /b 1
)

REM Setup if needed
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
)

if not exist .venv\Lib\site-packages\fastapi (
    echo Installing Python dependencies...
    .venv\Scripts\pip install -r requirements.txt
)

if not exist dashboard\node_modules (
    echo Installing Node dependencies...
    cd dashboard
    call npm install
    cd ..
)

REM Start Ollama if installed
where ollama >nul 2>&1
if not errorlevel 1 (
    echo Starting Ollama...
    start /b ollama serve >nul 2>&1
    timeout /t 3 /nobreak >nul
)

REM Start API Server
echo Starting API Server...
start "API Server" cmd /c ".venv\Scripts\python 19_API_Server.py"

timeout /t 3 /nobreak >nul

REM Start Dashboard
echo Starting Dashboard...
start "Dashboard" cmd /c "cd dashboard && npm run dev"

REM Start WebSocket
echo Starting WebSocket feeds...
start "WebSocket" cmd /c ".venv\Scripts\python 15_WebSocket_Real_Time_Feeds.py"

timeout /t 5 /nobreak >nul

echo.
echo ================================================
echo All systems starting...
echo ================================================
echo Dashboard:   http://localhost:5173
echo API Docs:    http://localhost:8000/docs
echo WebSocket:   ws://localhost:8765
echo.
echo Press any key to stop all services...
pause >nul

echo Stopping services...
taskkill /FI "WINDOWTITLE eq API Server" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Dashboard" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq WebSocket" /F >nul 2>&1

echo Done.
