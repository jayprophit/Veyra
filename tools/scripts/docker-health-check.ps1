# Health check for Docker Compose services
# Usage: .\tools\scripts\docker-health-check.ps1

$ErrorActionPreference = "Stop"

Write-Host "🏥 Checking Veyra Docker Compose health..." -ForegroundColor Cyan

try {
    $output = & docker compose ps
    Write-Host $output
    
    Write-Host "`n📊 Container Status:" -ForegroundColor Yellow
    
    $containers = @(
        "veyra-web",
        "veyra-api",
        "veyra-postgres",
        "veyra-redis",
        "veyra-qdrant",
        "veyra-adminer"
    )
    
    foreach ($container in $containers) {
        $status = & docker inspect -f "{{.State.Status}}" $container 2>&1
        if ($status -eq "running") {
            Write-Host "  ✅ $container : Running" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $container : $status" -ForegroundColor Red
        }
    }
    
    Write-Host "`n📋 Resource Usage:" -ForegroundColor Yellow
    & docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
