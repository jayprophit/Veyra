# Stop and remove Veyra Docker Compose stack
# Usage: .\tools\scripts\docker-compose-down.ps1

param(
    [switch]$RemoveVolumes = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🛑 Stopping Veyra Docker Compose stack..." -ForegroundColor Yellow

$downArgs = @("down")

if ($RemoveVolumes) {
    $downArgs += "-v"
    Write-Host "⚠️  Volumes will be removed!" -ForegroundColor Red
}

try {
    & docker compose @downArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Compose stack stopped" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker Compose down failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
