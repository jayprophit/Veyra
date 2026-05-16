# Start Veyra stack with Docker Compose
# Usage: .\tools\scripts\docker-compose-up.ps1

param(
    [switch]$Build = $false,
    [switch]$Detached = $true
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Veyra Docker Compose stack..." -ForegroundColor Cyan

$composeArgs = @("up")

if ($Build) {
    $composeArgs += "--build"
}

if ($Detached) {
    $composeArgs += "-d"
}

try {
    & docker compose @composeArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Compose stack started successfully" -ForegroundColor Green
        
        if ($Detached) {
            Write-Host "`nRunning services:" -ForegroundColor Yellow
            & docker compose ps
            
            Write-Host "`nAccess points:" -ForegroundColor Yellow
            Write-Host "  • Web App: http://localhost:3000" -ForegroundColor Cyan
            Write-Host "  • API Gateway: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "  • Database (Adminer): http://localhost:8080" -ForegroundColor Cyan
            Write-Host "  • PostgreSQL: localhost:5432" -ForegroundColor Cyan
            Write-Host "  • Redis: localhost:6379" -ForegroundColor Cyan
            Write-Host "  • Qdrant: http://localhost:6333" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Docker Compose failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
