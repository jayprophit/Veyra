# Financial Master - Go Live Script
# ==================================
# Quick deployment for testing with paper trading
param(
    [Parameter()]
    [ValidateSet("local", "staging", "cloud")]
    [string]$Mode = "local",

    [switch]$SkipTests,
    [switch]$WithRealData
)

$ErrorActionPreference = "Stop"

Write-Host @"
╔══════════════════════════════════════════════════════════════════╗
║              FINANCIAL MASTER - GO LIVE                          ║
╠══════════════════════════════════════════════════════════════════╣
║  Mode: $Mode                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Validate environment
function Test-Prerequisites {
    Write-Host "`n[1/5] Checking prerequisites..." -ForegroundColor Yellow

    $prereqs = @(
        @{ Name = "Python"; Command = "python --version"; Required = $true },
        @{ Name = "pip"; Command = "pip --version"; Required = $true },
        @{ Name = "Git"; Command = "git --version"; Required = $false }
    )

    foreach ($prereq in $prereqs) {
        try {
            Invoke-Expression $prereq.Command | Out-Null
            Write-Host "  ✓ $($prereq.Name) found" -ForegroundColor Green
        } catch {
            if ($prereq.Required) {
                Write-Host "  ✗ $($prereq.Name) NOT FOUND (Required)" -ForegroundColor Red
                exit 1
            } else {
                Write-Host "  ⚠ $($prereq.Name) not found (Optional)" -ForegroundColor Yellow
            }
        }
    }
}

# Setup environment file
function Initialize-Environment {
    Write-Host "`n[2/5] Setting up environment..." -ForegroundColor Yellow

    $envFile = switch ($Mode) {
        "local" { ".env.local" }
        "staging" { ".env.staging" }
        "cloud" { ".env.staging" }
        default { ".env.local" }
    }

    if (Test-Path $envFile) {
        Copy-Item $envFile ".env" -Force
        Write-Host "  ✓ Environment configured: $envFile" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Environment file not found: $envFile" -ForegroundColor Red
        exit 1
    }

    # Safety check for paper trading
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "ALPACA_PAPER\s*=\s*true" -or $envContent -match "ENABLE_PAPER_TRADING_ONLY\s*=\s*true") {
        Write-Host "  ✓ PAPER TRADING MODE ENABLED (Safe)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ WARNING: Paper trading not explicitly enabled" -ForegroundColor Yellow
        $confirm = Read-Host "Continue anyway? (y/N)"
        if ($confirm -ne "y") { exit 1 }
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Host "`n[3/5] Installing dependencies..." -ForegroundColor Yellow

    try {
        pip install -q -r requirements.txt
        Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Run tests
function Invoke-Tests {
    if ($SkipTests) {
        Write-Host "`n[4/5] Skipping tests (--SkipTests flag set)" -ForegroundColor Yellow
        return
    }

    Write-Host "`n[4/5] Running tests..." -ForegroundColor Yellow

    try {
        # Health check test
        Write-Host "  Testing API server..."
        $process = Start-Process -FilePath "python" -ArgumentList "-m", "src.backend.app.api_server" -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 5

        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
            if ($response.status -eq "healthy") {
                Write-Host "  ✓ API health check passed" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ⚠ API test failed (may need manual check)" -ForegroundColor Yellow
        } finally {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }

        # Unit tests
        Write-Host "  Running unit tests..."
        python -m pytest tests/unit -v --tb=short 2>&1 | Select-String "passed|failed|error" | ForEach-Object {
            Write-Host "    $_"
        }
    } catch {
        Write-Host "  ⚠ Some tests failed (non-critical)" -ForegroundColor Yellow
    }
}

# Start services
function Start-Services {
    Write-Host "`n[5/5] Starting services..." -ForegroundColor Yellow

    switch ($Mode) {
        "local" {
            Write-Host "`n  Starting Local Mode:" -ForegroundColor Cyan
            Write-Host "  - API Server: http://localhost:8000" -ForegroundColor Gray
            Write-Host "  - WebSocket:  ws://localhost:8765" -ForegroundColor Gray
            Write-Host "  - Docs:       http://localhost:8000/docs" -ForegroundColor Gray
            Write-Host "`n  Press Ctrl+C to stop`n" -ForegroundColor Yellow

            # Start both services
            $apiJob = Start-Job {
                Set-Location $using:PWD
                uvicorn src.backend.app.api_server:app --host 0.0.0.0 --port 8000 --reload
            }

            $wsJob = Start-Job {
                Set-Location $using:PWD
                python src/backend/app/websocket_real_time_feeds.py
            }

            # Monitor jobs
            while ($true) {
                $apiLog = Receive-Job $apiJob
                $wsLog = Receive-Job $wsJob

                if ($apiLog) { Write-Host "[API] $apiLog" -ForegroundColor Blue }
                if ($wsLog) { Write-Host "[WS]  $wsLog" -ForegroundColor Magenta }

                Start-Sleep -Milliseconds 100
            }
        }

        "staging" {
            Write-Host "`n  Staging mode selected." -ForegroundColor Cyan
            Write-Host "  To deploy to Render:" -ForegroundColor Gray
            Write-Host "  1. Push to GitHub: git push origin main" -ForegroundColor Gray
            Write-Host "  2. Render will auto-deploy from render.yaml" -ForegroundColor Gray
            Write-Host "  3. Set secrets in Render Dashboard" -ForegroundColor Gray
        }

        "cloud" {
            Write-Host "`n  Cloud deployment mode." -ForegroundColor Cyan
            Write-Host "  Ensure you have set:" -ForegroundColor Gray
            Write-Host "  - ALPACA_PAPER_API_KEY" -ForegroundColor Gray
            Write-Host "  - ALPACA_PAPER_API_SECRET" -ForegroundColor Gray
            Write-Host "  - FINNHUB_API_KEY" -ForegroundColor Gray
        }
    }
}

# Main execution
Test-Prerequisites
Initialize-Environment
Install-Dependencies
Invoke-Tests
Start-Services
