@echo off
REM Financial Master AI Engine Setup Script for Windows
REM Run this to install all dependencies and verify setup

echo ================================================================================
echo FINANCIAL MASTER AI/ML ENGINE - SETUP
echo ================================================================================
echo.
echo This script will:
echo 1. Check Python installation
echo 2. Install required packages
echo 3. Verify setup by running a test
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Python detected:
python --version
echo.

REM Install dependencies
echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Create directories
echo [3/4] Creating data directories...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist exports mkdir exports
echo [OK] Directories created
echo.

REM Run test
echo [4/4] Running setup test...
python -c "
import pandas
import numpy
import sklearn
import requests
import schedule
print('[OK] All imports successful')
print('[OK] Pandas version:', pandas.__version__)
print('[OK] NumPy version:', numpy.__version__)
print('[OK] Scikit-learn version:', sklearn.__version__)
"

if errorlevel 1 (
    echo ERROR: Import test failed
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SETUP COMPLETE
echo ================================================================================
echo.
echo Next steps:
echo 1. Run single cycle test: python 09_Autonomous_Master_Controller.py --mode single
echo 2. Edit configuration: 00_Master_System_Config.json
echo 3. Run full autonomous mode: python 09_Autonomous_Master_Controller.py --mode continuous
echo.
echo See README_SPREADSHEET_SYSTEM.txt for full documentation
echo.
pause
