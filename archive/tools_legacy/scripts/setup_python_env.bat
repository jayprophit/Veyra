@echo off
REM Windows Batch script to set up Python environment for Veyra
REM Resolves "Select Python Interpreter" issue in Windsurf/VS Code

echo ========================================
echo Veyra - Python Environment Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo Found: %PYTHON_VERSION%

REM Navigate to project root
cd /d "%~dp0\.."
echo Project root: %CD%

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment at .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists at .venv
)

REM Install dependencies
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    .venv\Scripts\pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo WARNING: Some dependencies failed to install
    ) else (
        echo Dependencies installed successfully!
    )
) else (
    echo WARNING: requirements.txt not found
)

REM Install development packages
echo Installing development packages...
.venv\Scripts\pip install pytest pytest-cov black flake8 mypy isort

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Restart Windsurf/VS Code
echo 2. Press Ctrl+Shift+P and run 'Python: Select Interpreter'
echo 3. Choose: %CD%\.venv\Scripts\python.exe
echo.
echo Or run the server directly:
echo   .venv\Scripts\python -m src.backend.app.api_server
echo.
pause
