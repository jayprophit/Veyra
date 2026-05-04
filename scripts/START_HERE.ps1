#!/usr/bin/env pwsh
# Financial Master - Quick Launcher
# ================================
# One command to start everything: Docker, WSL/Ubuntu, Ollama, and the app

param(
    [switch]$QuickStart,      # Start everything with defaults
    [switch]$WithAI,          # Include Ollama AI models
    [switch]$Stop,           # Stop all services
    [switch]$Status          # Check status
)

$ErrorActionPreference = "Stop"

# Colors
$Green = "`e[32m"
$Cyan = "`e[36m"
$Reset = "`e[0m"

function Show-Banner {
    Write-Host @"
$Green
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              🚀 FINANCIAL MASTER v2.50.0                      ║
║                                                               ║
║     Automated Infrastructure + AI-Powered Finance Platform     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
$Reset
"@
}

function Show-Help {
    Show-Banner
    Write-Host "QUICK START OPTIONS:`n" -ForegroundColor Cyan
    Write-Host "  .\START_HERE.ps1 -QuickStart    Start Docker + WSL + Financial Master"
    Write-Host "  .\START_HERE.ps1 -WithAI        Start everything + Ollama AI models"
    Write-Host "  .\START_HERE.ps1 -Stop          Stop all services"
    Write-Host "  .\START_HERE.ps1 -Status        Check infrastructure status"
    Write-Host ""
    Write-Host "ADVANCED OPTIONS:" -ForegroundColor Cyan
    Write-Host "  .\scripts\automate_infrastructure.ps1 -FullSetup"
    Write-Host "  .\scripts\automate_infrastructure.ps1 -StartDocker -StartOllama"
    Write-Host "  .\scripts\setup_ollama_models.ps1 -PullRecommended"
    Write-Host ""
    Write-Host "WSL/LINUX:" -ForegroundColor Cyan
    Write-Host "  ./scripts/automate_infrastructure.sh start"
    Write-Host "  ./scripts/automate_infrastructure.sh setup"
    Write-Host ""
}

# Main
if ($args.Count -eq 0 -and -not ($QuickStart -or $WithAI -or $Stop -or $Status)) {
    Show-Help
    exit 0
}

Show-Banner

if ($Stop) {
    .\scripts\automate_infrastructure.ps1 -StopAll
    exit 0
}

if ($Status) {
    .\scripts\automate_infrastructure.ps1 -Status
    exit 0
}

if ($QuickStart) {
    Write-Host "Starting Financial Master with standard setup..." -ForegroundColor Cyan
    .\scripts\automate_infrastructure.ps1 -FullSetup
}
elseif ($WithAI) {
    Write-Host "Starting Financial Master with AI (Ollama)..." -ForegroundColor Cyan
    
    # Start infrastructure
    .\scripts\automate_infrastructure.ps1 -StartDocker -SetupWSL
    
    # Start Ollama in WSL (better performance)
    .\scripts\automate_infrastructure.ps1 -StartOllama
    
    # Pull recommended models
    Write-Host "`n📦 Setting up AI models..." -ForegroundColor Cyan
    .\scripts\setup_ollama_models.ps1 -PullRecommended
    
    # Start with Ollama docker-compose
    $projectRoot = Resolve-Path "$PSScriptRoot"
    Set-Location $projectRoot
    
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
    }
    
    Write-Host "`n🐳 Starting Docker stack with AI services..." -ForegroundColor Cyan
    docker-compose -f docker-compose.yml -f docker-compose.ollama.yml --profile ai up --build -d
    
    Write-Host "`n✅ Financial Master with AI is running!" -ForegroundColor Green
    Write-Host "   API:       http://localhost:8000" -ForegroundColor White
    Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor White
    Write-Host "   Ollama:    http://localhost:11434" -ForegroundColor White
    Write-Host "   Grafana:   http://localhost:3001" -ForegroundColor White
}

Write-Host "`nUse '.\START_HERE.ps1 -Stop' to stop all services.`n" -ForegroundColor Gray
