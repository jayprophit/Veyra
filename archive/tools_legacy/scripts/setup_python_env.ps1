# PowerShell script to set up Python environment for Veyra
# Resolves "Select Python Interpreter" issue in Windsurf/VS Code

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Veyra - Python Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.9+ from https://python.org"
    exit 1
}

$pythonVersion = & $pythonCmd.Source --version
Write-Host "Found Python: $pythonVersion" -ForegroundColor Green

# Navigate to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Project root: $projectRoot" -ForegroundColor Gray

# Create virtual environment if it doesn't exist
$venvPath = Join-Path $projectRoot ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at .venv..." -ForegroundColor Yellow
    & $pythonCmd.Source -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists at .venv" -ForegroundColor Green
}

# Activate virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "Activated virtual environment" -ForegroundColor Green
} else {
    Write-Warning "Could not find activation script at $activateScript"
}

# Install dependencies
$requirementsPath = Join-Path $projectRoot "requirements.txt"
if (Test-Path $requirementsPath) {
    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    $pipPath = Join-Path $venvPath "Scripts\pip.exe"
    & $pipPath install -r $requirementsPath
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Some dependencies failed to install"
    } else {
        Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    }
} else {
    Write-Warning "requirements.txt not found at $requirementsPath"
}

# Install development dependencies
$devPackages = @("pytest", "pytest-cov", "black", "flake8", "mypy", "isort")
Write-Host "Installing development packages..." -ForegroundColor Yellow
$pipPath = Join-Path $venvPath "Scripts\pip.exe"
& $pipPath install $devPackages

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Restart Windsurf/VS Code" -ForegroundColor Yellow
Write-Host "2. Press Ctrl+Shift+P and run 'Python: Select Interpreter'" -ForegroundColor Yellow
Write-Host "3. Choose: $venvPath\Scripts\python.exe" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or run the server directly:" -ForegroundColor White
Write-Host "  .venv\Scripts\python -m src.backend.app.api_server" -ForegroundColor Cyan
Write-Host ""
