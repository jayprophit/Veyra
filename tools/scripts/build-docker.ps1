# Build Docker image for Veyra
# Usage: .\tools\scripts\build-docker.ps1

param(
    [string]$Tag = "latest",
    [switch]$NoBuildCache = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🐳 Building Veyra Docker image..." -ForegroundColor Cyan

$buildArgs = @(
    "build",
    "-t", "veyra:$Tag",
    "-f", "infrastructure/docker/web.Dockerfile",
    "."
)

if ($NoBuildCache) {
    $buildArgs += "--no-cache"
}

try {
    & docker @buildArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker image built successfully: veyra:$Tag" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker build failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
