# Full automation: Build, Start, and Monitor
# Usage: .\tools\scripts\full-automation.ps1

param(
    [switch]$SkipBuild = $false,
    [switch]$WithAI = $false,
    [switch]$Watch = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🤖 FULL AUTOMATION - Veyra Docker Stack" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Step 1: Build
if (-not $SkipBuild) {
    Write-Host "`n[1/4] 🔨 Building Docker image..." -ForegroundColor Yellow
    try {
        & docker build -t veyra:latest -f infrastructure/docker/web.Dockerfile .
        Write-Host "✅ Build completed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Build failed: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n[1/4] ⏭️  Skipping build (using existing image)" -ForegroundColor Yellow
}

# Step 2: Start services
Write-Host "`n[2/4] 🚀 Starting Docker Compose stack..." -ForegroundColor Yellow
try {
    $profile = if ($WithAI) { "--profile ai" } else { "" }
    Invoke-Expression "docker compose up -d $profile"
    Write-Host "✅ Stack started" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Wait for health checks
Write-Host "`n[3/4] 🏥 Waiting for services to be healthy..." -ForegroundColor Yellow
$maxWait = 60
$waited = 0
while ($waited -lt $maxWait) {
    $pgHealth = & docker inspect veyra-postgres --format "{{.State.Health.Status}}" 2>$null
    $redisHealth = & docker inspect veyra-redis --format "{{.State.Health.Status}}" 2>$null
    
    if ($pgHealth -eq "healthy" -and $redisHealth -eq "healthy") {
        Write-Host "✅ All services healthy" -ForegroundColor Green
        break
    }
    
    Write-Host "⏳ Waiting... (${waited}s/${maxWait}s)" -ForegroundColor Gray
    Start-Sleep -Seconds 5
    $waited += 5
}

if ($waited -ge $maxWait) {
    Write-Host "⚠️  Health check timeout - services may still be starting" -ForegroundColor Yellow
}

# Step 4: Display status
Write-Host "`n[4/4] 📊 Current status..." -ForegroundColor Yellow
& docker compose ps

# Final summary
Write-Host "`n✨ AUTOMATION COMPLETE" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "`n📍 Access your application:" -ForegroundColor Cyan
Write-Host "  • http://localhost:3000  (Web App)" -ForegroundColor White
Write-Host "  • http://localhost:8080  (Database Admin)" -ForegroundColor White
Write-Host "  • http://localhost:6333  (Qdrant Vector DB)" -ForegroundColor White
if ($WithAI) {
    Write-Host "  • http://localhost:11434 (Ollama AI)" -ForegroundColor White
}

Write-Host "`n🛠️  Management commands:" -ForegroundColor Cyan
Write-Host "  • View logs:    docker compose logs -f" -ForegroundColor Gray
Write-Host "  • Stop:         docker compose down" -ForegroundColor Gray
Write-Host "  • Restart:      docker compose restart" -ForegroundColor Gray
Write-Host "  • Execute cmd:  docker compose exec web sh" -ForegroundColor Gray

if ($Watch) {
    Write-Host "`n👀 Monitoring logs (Ctrl+C to exit)..." -ForegroundColor Yellow
    & docker compose logs -f web api
}
