# Quick fix script - Run this first!
# Fixes the most common issues immediately

Write-Host "FINANCIAL MASTER - QUICK FIX" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

# Navigate to project root
$scriptPath = $PSScriptRoot
$projectRoot = Split-Path -Parent $scriptPath

Write-Host "Project: $projectRoot" -ForegroundColor Gray
Write-Host ""

# 1. Check if we're in the right directory
if (-not (Test-Path (Join-Path $projectRoot "src"))) {
    Write-Error "ERROR: Not in Veyra project directory!"
    Write-Host "Please run this script from the Veyra folder." -ForegroundColor Red
    exit 1
}

# 2. Set execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# 3. Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python not found! Install from https://python.org"
    exit 1
}
Write-Host "   Found: $($python.Source)" -ForegroundColor Green

# 4. Create virtual environment
Write-Host ""
Write-Host "2. Setting up virtual environment..." -ForegroundColor Yellow
$venvPath = Join-Path $projectRoot ".venv"

if (-not (Test-Path $venvPath)) {
    & python -m venv $venvPath
    Write-Host "   Created .venv" -ForegroundColor Green
} else {
    Write-Host "   .venv exists" -ForegroundColor Green
}

# 5. Activate and install
Write-Host ""
Write-Host "3. Installing dependencies..." -ForegroundColor Yellow
$pipPath = Join-Path $venvPath "Scripts\pip.exe"

# Upgrade pip
& $pipPath install --upgrade pip | Out-Null

# Install requirements
$reqFile = Join-Path $projectRoot "requirements.txt"
if (Test-Path $reqFile) {
    & $pipPath install -r $reqFile | Out-Null
    Write-Host "   Dependencies installed" -ForegroundColor Green
}

# 6. Run basic test
Write-Host ""
Write-Host "4. Verifying setup..." -ForegroundColor Yellow
$pythonPath = Join-Path $venvPath "Scripts\python.exe"
$testResult = & $pythonPath -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}'); print('OK')" 2>&1

if ($testResult -match "OK") {
    Write-Host "   $testResult" -ForegroundColor Green
} else {
    Write-Warning "Setup verification had issues"
}

Write-Host ""
Write-Host "============================" -ForegroundColor Cyan
Write-Host "QUICK FIX COMPLETE!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the server:" -ForegroundColor White
Write-Host "  $projectRoot\.venv\Scripts\python -m src.backend.app.api_server" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run tests:" -ForegroundColor White
Write-Host "  $projectRoot\.venv\Scripts\pytest tests/ -v" -ForegroundColor Cyan
Write-Host ""
