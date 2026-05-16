param(
    [switch]$StopDesktopKubernetes
)

$ErrorActionPreference = "Stop"

Write-Host "Current Docker CPU snapshot"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

Write-Host ""
Write-Host "Stopping optional Veyra services that are not needed for the core private runtime..."
cmd /c "docker compose stop qdrant adminer >nul 2>&1"

if ($StopDesktopKubernetes) {
    Write-Host "Stopping Docker Desktop Kubernetes helper containers..."
    foreach ($name in @("desktop-control-plane", "kind-cloud-provider", "kind-registry-mirror")) {
        $container = docker ps -a --filter "name=^/$name$" --format "{{.Names}}"
        if ($container) {
            cmd /c "docker stop $name >nul 2>&1"
        }
    }
}

Write-Host ""
Write-Host "Reduced Docker CPU snapshot"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
