# Quick start Veyra without building (uses cached image)
# Usage: .\tools\scripts\quick-start.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Quick Starting Veyra Docker Stack..." -ForegroundColor Cyan

try {
    Write-Host "📦 Pulling latest images..." -ForegroundColor Yellow
    & docker compose pull --ignore-pull-failures
    
    Write-Host "`n🔧 Starting services..." -ForegroundColor Yellow
    & docker compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Stack started successfully!" -ForegroundColor Green
        
        Write-Host "`n⏳ Waiting for services to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        Write-Host "`n🏥 Checking service health..." -ForegroundColor Yellow
        & docker compose ps
        
        Write-Host "`n📍 Access points:" -ForegroundColor Cyan
        Write-Host "  • Web App: http://localhost:3000" -ForegroundColor White
        Write-Host "  • Database Admin: http://localhost:8080" -ForegroundColor White
        Write-Host "  • PostgreSQL: localhost:5432" -ForegroundColor White
        Write-Host "  • Redis: localhost:6379" -ForegroundColor White
        Write-Host "  • Qdrant: http://localhost:6333" -ForegroundColor White
        
        Write-Host "`n💡 View logs: docker compose logs -f web api" -ForegroundColor Yellow
        Write-Host "💡 Stop stack: docker compose down" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Failed to start stack" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
