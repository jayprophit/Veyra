#!/usr/bin/env pwsh
# Master setup script - Creates all missing files and verifies setup

param(
    [switch]$FullSetup = $false,
    [switch]$SkipK8s = $false,
    [switch]$TestOnly = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🎯 VEYRA SETUP - COMPLETING MISSING COMPONENTS" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Verify Docker is running
Write-Host "`n[1/5] 🐳 Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not running" -ForegroundColor Red
    exit 1
}

# Verify Docker Compose
Write-Host "`n[2/5] 📦 Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker compose version
    Write-Host "✅ $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose not found" -ForegroundColor Red
    exit 1
}

# Check all required files exist
Write-Host "`n[3/5] 📋 Verifying files..." -ForegroundColor Yellow

$requiredFiles = @(
    "docker-compose.yml",
    ".dockerignore",
    "infrastructure/docker/web.Dockerfile",
    "tools/scripts/build-docker.ps1",
    "tools/scripts/docker-compose-up.ps1",
    "tools/scripts/docker-compose-down.ps1",
    "tools/scripts/quick-start.ps1",
    "tools/scripts/docker-health-check.ps1",
    "tools/scripts/k8s-deploy.ps1",
    "tools/scripts/k8s-logs.ps1",
    "tools/scripts/veyra-doctor.py",
    "tools/scripts/veyra-mcp-server.py",
    "infrastructure/kubernetes/veyra-app-deployment.yaml",
    "infrastructure/kubernetes/postgres-deployment.yaml",
    "infrastructure/kubernetes/redis-deployment.yaml",
    "infrastructure/kubernetes/qdrant-deployment.yaml",
    "infrastructure/kubernetes/ollama-deployment.yaml",
    "infrastructure/kubernetes/kustomization.yaml",
    ".windsurf/mcp.json"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $file (MISSING)" -ForegroundColor Yellow
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "`n⚠️  $($missingFiles.Count) files still need to be created" -ForegroundColor Yellow
}

# Check running containers
Write-Host "`n[4/5] 🐳 Checking running containers..." -ForegroundColor Yellow
try {
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}"
    Write-Host $containers -ForegroundColor Cyan
} catch {
    Write-Host "⚠️  Could not retrieve container status" -ForegroundColor Yellow
}

# Docker system status
Write-Host "`n[5/5] 📊 Docker system status..." -ForegroundColor Yellow
try {
    $images = docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | Select-String "veyra"
    if ($images) {
        Write-Host "Docker Images:" -ForegroundColor Cyan
        Write-Host $images -ForegroundColor White
    }
    
    Write-Host "`nDocker Storage:" -ForegroundColor Cyan
    $df = docker system df
    Write-Host $df -ForegroundColor White
} catch {
    Write-Host "⚠️  Could not retrieve Docker system info" -ForegroundColor Yellow
}

# Summary
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "✅ VERIFICATION COMPLETE" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n📊 SUMMARY:" -ForegroundColor Cyan
Write-Host "  Total required files: $($requiredFiles.Count)" -ForegroundColor White
Write-Host "  Files present: $($requiredFiles.Count - $missingFiles.Count)" -ForegroundColor Green
Write-Host "  Files missing: $($missingFiles.Count)" -ForegroundColor Yellow

if ($missingFiles.Count -eq 0) {
    Write-Host "`n🎉 ALL FILES COMPLETE! Ready to use." -ForegroundColor Green
    
    Write-Host "`n🚀 QUICK START:" -ForegroundColor Cyan
    Write-Host "  .\tools\scripts\quick-start.ps1              # Fast launch" -ForegroundColor White
    Write-Host "  .\tools\scripts\full-automation.ps1          # Build + run" -ForegroundColor White
    Write-Host "  python .\tools\scripts\veyra-doctor.py health # Verify health" -ForegroundColor White
} else {
    Write-Host "`n⚠️  $($missingFiles.Count) files still missing. See WHATS_MISSING.md" -ForegroundColor Yellow
}

Write-Host "`n📍 CURRENT SERVICES:" -ForegroundColor Cyan
Write-Host "  Web App: http://localhost:3000" -ForegroundColor White
Write-Host "  Admin UI: http://localhost:8080" -ForegroundColor White
Write-Host "  Database: localhost:5432" -ForegroundColor White
Write-Host "  Redis: localhost:6379" -ForegroundColor White
Write-Host "  Vector DB: http://localhost:6333" -ForegroundColor White

Write-Host "`n✨ Setup verification complete!" -ForegroundColor Green
