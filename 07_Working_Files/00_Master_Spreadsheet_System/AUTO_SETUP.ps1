# Financial Master - Automated Setup Script (PowerShell)
# Run: .\AUTO_SETUP.ps1

param(
    [switch]$FullSetup,
    [switch]$OllamaOnly,
    [switch]$DockerOnly,
    [switch]$DashboardOnly
)

$ErrorActionPreference = "Stop"

function Write-Header($text) {
    Write-Host "`n================================================" -ForegroundColor Cyan
    Write-Host $text -ForegroundColor Cyan
    Write-Host "================================================`n" -ForegroundColor Cyan
}

function Test-Command($cmd) {
    return [bool](Get-Command -Name $cmd -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Header "Checking Prerequisites"

$checks = @{
    "PowerShell" = $true
    "WSL" = Test-Command wsl
    "Docker" = Test-Command docker
    "Ollama" = Test-Command ollama
    "Python" = Test-Command python
    "Node.js" = Test-Command npm
    "Git" = Test-Command git
}

foreach ($check in $checks.GetEnumerator()) {
    $status = if ($check.Value) { "✓" } else { "✗" }
    $color = if ($check.Value) { "Green" } else { "Yellow" }
    Write-Host "  $status $($check.Key)" -ForegroundColor $color
}

# Ollama Setup
if ($FullSetup -or $OllamaOnly) {
    Write-Header "Setting up Ollama"
    
    if (!(Test-Command ollama)) {
        Write-Host "Installing Ollama..." -ForegroundColor Yellow
        winget install Ollama.Ollama --silent --accept-package-agreements
    }
    
    Write-Host "Starting Ollama server..." -ForegroundColor Green
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    
    $models = @("llama3.2:3b", "llama3.1:8b", "qwen2.5:7b", "nomic-embed-text")
    foreach ($model in $models) {
        Write-Host "Downloading $model..." -ForegroundColor Cyan
        ollama pull $model
    }
    
    Write-Host "✓ Ollama ready with models: $models" -ForegroundColor Green
}

# Docker Setup
if ($FullSetup -or $DockerOnly) {
    Write-Header "Setting up Docker"
    
    if (!(Test-Command docker)) {
        Write-Host "Docker not found. Please install Docker Desktop." -ForegroundColor Red
        Start-Process "https://www.docker.com/products/docker-desktop"
    } else {
        Write-Host "Starting Docker Compose stack..." -ForegroundColor Green
        docker-compose up -d
        Write-Host "✓ Docker stack running" -ForegroundColor Green
    }
}

# Dashboard Setup
if ($FullSetup -or $DashboardOnly) {
    Write-Header "Setting up React Dashboard"
    
    Set-Location dashboard
    
    if (!(Test-Path node_modules)) {
        Write-Host "Installing npm dependencies..." -ForegroundColor Cyan
        npm install
    }
    
    Write-Host "Starting development server..." -ForegroundColor Green
    Start-Process npm -ArgumentList "run dev" -WindowStyle Hidden
    
    Set-Location ..
    Write-Host "✓ Dashboard starting at http://localhost:5173" -ForegroundColor Green
}

# Python Environment
if ($FullSetup) {
    Write-Header "Setting up Python Environment"
    
    if (!(Test-Path .venv)) {
        Write-Host "Creating virtual environment..." -ForegroundColor Cyan
        python -m venv .venv
    }
    
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    .venv\Scripts\pip install -r requirements.txt
    
    Write-Host "✓ Python environment ready" -ForegroundColor Green
}

# Final Summary
Write-Header "Setup Complete!"

Write-Host "🌐 Dashboard: http://localhost:5173" -ForegroundColor Cyan
Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🤖 Ollama: http://localhost:11434" -ForegroundColor Cyan
Write-Host "🐳 Docker: docker-compose ps" -ForegroundColor Cyan

Write-Host "`nUseful commands:" -ForegroundColor Yellow
Write-Host "  python 19_API_Server.py    # Start API" -ForegroundColor Gray
Write-Host "  python main.py             # Start all systems" -ForegroundColor Gray
Write-Host "  ollama list                # Check models" -ForegroundColor Gray
Write-Host "  docker-compose logs -f     # View logs" -ForegroundColor Gray
