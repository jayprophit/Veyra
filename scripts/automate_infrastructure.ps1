#!/usr/bin/env pwsh
# Financial Master - Infrastructure Automation
# =============================================
# Automates Docker, WSL2/Ubuntu, and Ollama setup
# Run: .\scripts\automate_infrastructure.ps1

param(
    [switch]$StartDocker,
    [switch]$StartOllama,
    [switch]$SetupWSL,
    [switch]$FullSetup,
    [switch]$StopAll,
    [switch]$Status
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Colors
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-Status { param([string]$Message, [string]$Status)
    switch ($Status) {
        "success" { Write-Host "$Green✓$Reset $Message" }
        "error" { Write-Host "$Red✗$Reset $Message" }
        "warning" { Write-Host "$Yellow⚠$Reset $Message" }
        "info" { Write-Host "$Blueℹ$Reset $Message" }
        default { Write-Host "  $Message" }
    }
}

# ============================================================================
# Docker Management
# ============================================================================

function Test-DockerRunning {
    try {
        $null = docker version 2>$null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

function Start-DockerDesktop {
    Write-Status "Checking Docker Desktop..." "info"
    
    if (Test-DockerRunning) {
        Write-Status "Docker is already running" "success"
        return $true
    }
    
    # Try to start Docker Desktop
    $dockerPath = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Write-Status "Starting Docker Desktop..." "info"
        Start-Process $dockerPath
        
        # Wait for Docker to be ready
        $maxWait = 60
        $waited = 0
        while (-not (Test-DockerRunning) -and $waited -lt $maxWait) {
            Start-Sleep -Seconds 2
            $waited += 2
            Write-Host "." -NoNewline
        }
        Write-Host ""
        
        if (Test-DockerRunning) {
            Write-Status "Docker Desktop started successfully" "success"
            return $true
        } else {
            Write-Status "Docker Desktop failed to start within ${maxWait}s" "error"
            return $false
        }
    } else {
        Write-Status "Docker Desktop not found at $dockerPath" "error"
        Write-Status "Please install Docker Desktop from https://docker.com" "warning"
        return $false
    }
}

# ============================================================================
# WSL2 / Ubuntu Management
# ============================================================================

function Test-WSLAvailable {
    try {
        $result = wsl -l -v 2>&1
        return $result -match "Ubuntu"
    } catch { return $false }
}

function Test-UbuntuRunning {
    try {
        $result = wsl -l -v 2>&1 | Select-String "Ubuntu.*Running"
        return $null -ne $result
    } catch { return $false }
}

function Start-UbuntuWSL {
    Write-Status "Checking WSL2 Ubuntu..." "info"
    
    if (-not (Test-WSLAvailable)) {
        Write-Status "Ubuntu not found in WSL. Installing..." "warning"
        
        # Enable WSL if needed
        wsl --install -d Ubuntu
        Write-Status "WSL2 Ubuntu installation started. Please complete setup in the new window." "warning"
        Write-Status "After Ubuntu setup completes, re-run this script." "info"
        return $false
    }
    
    if (Test-UbuntuRunning) {
        Write-Status "WSL2 Ubuntu is already running" "success"
        return $true
    }
    
    Write-Status "Starting WSL2 Ubuntu..." "info"
    wsl -d Ubuntu -e true
    
    Start-Sleep -Seconds 2
    
    if (Test-UbuntuRunning) {
        Write-Status "WSL2 Ubuntu started successfully" "success"
        return $true
    } else {
        Write-Status "Failed to start WSL2 Ubuntu" "error"
        return $false
    }
}

function Install-WSLDependencies {
    Write-Status "Installing dependencies in WSL2 Ubuntu..." "info"
    
    $commands = @(
        "sudo apt-get update -qq",
        "sudo apt-get install -y -qq curl wget git build-essential python3 python3-pip python3-venv nodejs npm",
        "sudo apt-get install -y -qq sqlite3 postgresql-client redis-tools",
        "sudo snap install docker"
    )
    
    foreach ($cmd in $commands) {
        Write-Host "  Running: $cmd" -ForegroundColor Gray
        $result = wsl -d Ubuntu -e bash -c $cmd 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Status "Command failed: $cmd" "warning"
        }
    }
    
    Write-Status "WSL2 dependencies installed" "success"
}

# ============================================================================
# Ollama Management
# ============================================================================

function Test-OllamaRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 2 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch { return $false }
}

function Test-OllamaInWSL {
    try {
        $result = wsl -d Ubuntu -e bash -c "curl -s http://localhost:11434/api/tags" 2>&1
        return $result -match "llama"
    } catch { return $false }
}

function Start-OllamaWindows {
    Write-Status "Checking Ollama (Windows)..." "info"
    
    if (Test-OllamaRunning) {
        Write-Status "Ollama is already running on localhost:11434" "success"
        return $true
    }
    
    # Check if Ollama is installed
    $ollamaPath = "${env:LOCALAPPDATA}\Programs\Ollama\ollama.exe"
    if (-not (Test-Path $ollamaPath)) {
        Write-Status "Ollama not found. Install from https://ollama.com" "warning"
        return $false
    }
    
    Write-Status "Starting Ollama..." "info"
    Start-Process $ollamaPath -WindowStyle Hidden
    
    # Wait for Ollama to be ready
    $maxWait = 30
    $waited = 0
    while (-not (Test-OllamaRunning) -and $waited -lt $maxWait) {
        Start-Sleep -Seconds 2
        $waited += 2
        Write-Host "." -NoNewline
    }
    Write-Host ""
    
    if (Test-OllamaRunning) {
        Write-Status "Ollama started successfully" "success"
        return $true
    } else {
        Write-Status "Ollama failed to start within ${maxWait}s" "error"
        return $false
    }
}

function Start-OllamaWSL {
    Write-Status "Checking Ollama in WSL2..." "info"
    
    # Check if Ollama is installed in WSL
    $checkResult = wsl -d Ubuntu -e bash -c "which ollama" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Installing Ollama in WSL2..." "info"
        $installCmd = "curl -fsSL https://ollama.com/install.sh | sh"
        wsl -d Ubuntu -e bash -c $installCmd
    }
    
    # Check if Ollama is running
    $isRunning = wsl -d Ubuntu -e bash -c "pgrep ollama" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Starting Ollama in WSL2..." "info"
        wsl -d Ubuntu -e bash -c "nohup ollama serve > /tmp/ollama.log 2>&1 &"
        Start-Sleep -Seconds 3
    }
    
    # Pull recommended models
    $models = @("llama3.2:3b", "llama3.1:8b")
    foreach ($model in $models) {
        Write-Status "Pulling Ollama model: $model..." "info"
        wsl -d Ubuntu -e bash -c "ollama pull $model" 2>&1 | Out-Null
    }
    
    Write-Status "Ollama is ready in WSL2" "success"
    return $true
}

function Get-OllamaModels {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5 -UseBasicParsing
        $models = $response.Content | ConvertFrom-Json
        return $models.models | ForEach-Object { $_.name }
    } catch {
        return @()
    }
}

# ============================================================================
# Financial Master Stack Management
# ============================================================================

function Start-FinancialMasterStack {
    param(
        [switch]$UseWSL,
        [switch]$UseDocker
    )
    
    Write-Status "Starting Financial Master stack..." "info"
    
    $projectRoot = Resolve-Path "$PSScriptRoot\.."
    
    if ($UseDocker) {
        # Start using Docker Compose
        Set-Location $projectRoot
        
        # Check if .env exists
        if (-not (Test-Path ".env")) {
            if (Test-Path ".env.example") {
                Copy-Item ".env.example" ".env"
                Write-Status "Created .env from template" "success"
            }
        }
        
        Write-Status "Building and starting Docker containers..." "info"
        docker-compose up --build -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Financial Master Docker stack is running" "success"
            Write-Status "API: http://localhost:8000" "info"
            Write-Status "Frontend: http://localhost:3000" "info"
            Write-Status "Grafana: http://localhost:3001" "info"
        } else {
            Write-Status "Failed to start Docker stack" "error"
        }
    } 
    elseif ($UseWSL) {
        # Start using WSL
        $projectPath = "/mnt/$($projectRoot.Drive.Name.ToLower())/$($projectRoot.Path.Substring(3).Replace('\', '/'))"
        
        wsl -d Ubuntu -e bash -c "cd $projectPath && python3 -m src.backend.app.api.unified_api &"
        Write-Status "Financial Master API started in WSL" "success"
    }
}

function Stop-AllServices {
    Write-Status "Stopping all Financial Master services..." "info"
    
    # Stop Docker containers
    Set-Location "$PSScriptRoot\.."
    docker-compose down 2>$null
    Write-Status "Docker containers stopped" "success"
    
    # Stop Ollama processes (Windows)
    Get-Process | Where-Object { $_.ProcessName -eq "ollama" } | Stop-Process -Force 2>$null
    Write-Status "Ollama (Windows) stopped" "success"
    
    # Stop Ollama in WSL
    wsl -d Ubuntu -e bash -c "pkill ollama" 2>$null
    Write-Status "Ollama (WSL) stopped" "success"
    
    Write-Status "All services stopped" "success"
}

function Get-InfrastructureStatus {
    Write-Host "`n========================================" -ForegroundColor Blue
    Write-Host "  Financial Master - Infrastructure Status" -ForegroundColor Blue
    Write-Host "========================================`n" -ForegroundColor Blue
    
    # Docker
    if (Test-DockerRunning) {
        Write-Status "Docker Desktop: Running" "success"
    } else {
        Write-Status "Docker Desktop: Stopped" "error"
    }
    
    # WSL
    if (Test-WSLAvailable) {
        if (Test-UbuntuRunning) {
            Write-Status "WSL2 Ubuntu: Running" "success"
        } else {
            Write-Status "WSL2 Ubuntu: Installed but stopped" "warning"
        }
    } else {
        Write-Status "WSL2 Ubuntu: Not installed" "error"
    }
    
    # Ollama
    if (Test-OllamaRunning) {
        Write-Status "Ollama (Windows): Running on :11434" "success"
        $models = Get-OllamaModels
        if ($models.Count -gt 0) {
            Write-Host "    Models: $($models -join ', ')" -ForegroundColor Gray
        }
    } else {
        Write-Status "Ollama (Windows): Not running" "warning"
    }
    
    if (Test-OllamaInWSL) {
        Write-Status "Ollama (WSL): Running" "success"
    } else {
        Write-Status "Ollama (WSL): Not running or not installed" "warning"
    }
    
    # Docker containers
    if (Test-DockerRunning) {
        $containers = docker ps --format "table {{.Names}}\t{{.Status}}" 2>$null | Select-String "financial-master"
        if ($containers) {
            Write-Status "Financial Master containers:" "info"
            $containers | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
        }
    }
    
    Write-Host ""
}

# ============================================================================
# Main Execution
# ============================================================================

function Show-Help {
    Write-Host "`nFinancial Master - Infrastructure Automation" -ForegroundColor Blue
    Write-Host "=============================================" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Usage: .\scripts\automate_infrastructure.ps1 [Options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -StartDocker    Start Docker Desktop"
    Write-Host "  -StartOllama    Start Ollama service"
    Write-Host "  -SetupWSL       Setup WSL2 Ubuntu environment"
    Write-Host "  -FullSetup      Complete setup (Docker + WSL + Ollama + Stack)"
    Write-Host "  -StopAll        Stop all services"
    Write-Host "  -Status         Show infrastructure status"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host '  .\scripts\automate_infrastructure.ps1 -FullSetup'
    Write-Host '  .\scripts\automate_infrastructure.ps1 -Status'
    Write-Host '  .\scripts\automate_infrastructure.ps1 -StartDocker -StartOllama'
    Write-Host ""
}

# Main
if ($args.Count -eq 0 -and -not ($StartDocker -or $StartOllama -or $SetupWSL -or $FullSetup -or $StopAll -or $Status)) {
    Show-Help
    exit 0
}

if ($Status) {
    Get-InfrastructureStatus
    exit 0
}

if ($StopAll) {
    Stop-AllServices
    exit 0
}

if ($FullSetup) {
    Write-Host "`n🚀 Starting Full Financial Master Setup...`n" -ForegroundColor Cyan
    
    $dockerReady = Start-DockerDesktop
    $wslReady = Start-UbuntuWSL
    
    if ($wslReady) {
        Install-WSLDependencies
        Start-OllamaWSL
    } else {
        Start-OllamaWindows
    }
    
    if ($dockerReady) {
        Start-FinancialMasterStack -UseDocker
    }
    
    Write-Host "`n✅ Full setup complete!" -ForegroundColor Green
    Get-InfrastructureStatus
}
else {
    if ($StartDocker) { Start-DockerDesktop }
    if ($SetupWSL) { 
        Start-UbuntuWSL
        Install-WSLDependencies
    }
    if ($StartOllama) { 
        $wslReady = Test-UbuntuRunning
        if ($wslReady) {
            Start-OllamaWSL
        } else {
            Start-OllamaWindows
        }
    }
}
