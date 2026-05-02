#!/usr/bin/env pwsh
# Financial Master - Ollama Model Manager
# ======================================
# Manage Ollama models for AI features
# Run: .\scripts\setup_ollama_models.ps1

param(
    [switch]$PullRecommended,
    [switch]$PullAll,
    [switch]$ListModels,
    [switch]$RemoveAll,
    [string]$PullModel = ""
)

$ErrorActionPreference = "Stop"

# Colors
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-Status {
    param([string]$Message, [string]$Status)
    switch ($Status) {
        "success" { Write-Host "$Green✓$Reset $Message" }
        "error" { Write-Host "$Red✗$Reset $Message" }
        "warning" { Write-Host "$Yellow⚠$Reset $Message" }
        "info" { Write-Host "$Blueℹ$Reset $Message" }
        "header" { Write-Host "$Blue$Message$Reset" }
        default { Write-Host "  $Message" }
    }
}

function Test-OllamaRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 2 -UseBasicParsing
        return $response.StatusCode -eq 200
    }
    catch { return $false }
}

function Get-OllamaModels {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5 -UseBasicParsing
        $data = $response.Content | ConvertFrom-Json
        return $data.models
    }
    catch {
        return @()
    }
}

function Invoke-OllamaAPI {
    param([string]$Method, [string]$Endpoint, [object]$Body = $null)
    
    $uri = "http://localhost:11434$Endpoint"
    $headers = @{ "Content-Type" = "application/json" }
    
    try {
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json
            return Invoke-WebRequest -Uri $uri -Method $Method -Headers $headers -Body $jsonBody -UseBasicParsing
        }
        else {
            return Invoke-WebRequest -Uri $uri -Method $Method -Headers $headers -UseBasicParsing
        }
    }
    catch {
        Write-Status "API call failed: $_" "error"
        return $null
    }
}

function Install-OllamaModel {
    param([string]$ModelName)
    
    Write-Status "Pulling model: $ModelName..." "info"
    
    # Use Ollama CLI if available
    $ollamaPath = "${env:LOCALAPPDATA}\Programs\Ollama\ollama.exe"
    if (Test-Path $ollamaPath) {
        & $ollamaPath pull $ModelName
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Successfully pulled $ModelName" "success"
            return $true
        }
    }
    
    # Fallback to API
    $response = Invoke-OllamaAPI -Method "POST" -Endpoint "/api/pull" -Body @{ name = $ModelName }
    if ($response -and $response.StatusCode -eq 200) {
        Write-Status "Successfully pulled $ModelName" "success"
        return $true
    }
    else {
        Write-Status "Failed to pull $ModelName" "error"
        return $false
    }
}

# Recommended models for Financial Master
$RecommendedModels = @(
    @{
        Name        = "llama3.2:3b"
        Description = "Fast, efficient for simple analysis"
        UseCase     = "Quick summaries, simple Q&A"
    },
    @{
        Name        = "llama3.1:8b"
        Description = "More powerful, better reasoning"
        UseCase     = "Complex analysis, reports"
    },
    @{
        Name        = "mistral:7b"
        Description = "Good balance of speed/quality"
        UseCase     = "General purpose analysis"
    },
    @{
        Name        = "codellama:7b"
        Description = "Code-focused, good for data"
        UseCase     = "Data processing scripts"
    }
)

$AllModels = @(
    "llama3.2:3b", "llama3.2:1b",
    "llama3.1:8b", "llama3.1:70b",
    "mistral:7b", "mistral:7b-instruct",
    "codellama:7b", "codellama:13b",
    "qwen2.5:7b", "qwen2.5:14b",
    "gemma2:2b", "gemma2:9b",
    "phi3:mini", "phi3:medium"
)

# Main execution
if (-not (Test-OllamaRunning)) {
    Write-Status "Ollama is not running on localhost:11434" "error"
    Write-Status "Start Ollama first with: .\scripts\automate_infrastructure.ps1 -StartOllama" "info"
    exit 1
}

if ($ListModels) {
    $models = Get-OllamaModels
    if ($models.Count -eq 0) {
        Write-Status "No models installed" "warning"
    }
    else {
        Write-Host "`nInstalled Models:" -ForegroundColor Blue
        foreach ($model in $models) {
            $size = if ($model.size) { "($([math]::Round($model.size / 1GB, 1)) GB)" } else { "" }
            Write-Host "  • $($model.name) $size" -ForegroundColor White
        }
    }
    Write-Host ""
    exit 0
}

if ($PullModel) {
    Install-OllamaModel -ModelName $PullModel
    exit 0
}

if ($PullRecommended) {
    Write-Host "`n📦 Pulling Recommended Models for Financial Master" -ForegroundColor Cyan
    Write-Host "==================================================`n" -ForegroundColor Cyan
    
    foreach ($model in $RecommendedModels) {
        Write-Host "Model: $($model.Name)" -ForegroundColor Yellow
        Write-Host "  Description: $($model.Description)"
        Write-Host "  Use Case: $($model.UseCase)"
        Write-Host ""
        Install-OllamaModel -ModelName $model.Name
        Write-Host ""
    }
    
    Write-Status "All recommended models pulled!" "success"
}

if ($PullAll) {
    Write-Warning "This will pull all $($AllModels.Count) models which requires significant disk space (~50+ GB)"
    $confirm = Read-Host "Continue? (y/N)"
    if ($confirm -ne 'y') {
        exit 0
    }
    
    foreach ($model in $AllModels) {
        Install-OllamaModel -ModelName $model
    }
}

if ($RemoveAll) {
    $models = Get-OllamaModels
    if ($models.Count -eq 0) {
        Write-Status "No models to remove" "info"
        exit 0
    }
    
    Write-Warning "This will remove all $($models.Count) installed models"
    $confirm = Read-Host "Continue? (y/N)"
    if ($confirm -ne 'y') {
        exit 0
    }
    
    foreach ($model in $models) {
        Write-Status "Removing $($model.name)..." "info"
        $ollamaPath = "${env:LOCALAPPDATA}\Programs\Ollama\ollama.exe"
        if (Test-Path $ollamaPath) {
            & $ollamaPath rm $model.name
        }
    }
    
    Write-Status "All models removed" "success"
}

if (-not ($PullRecommended -or $PullAll -or $ListModels -or $RemoveAll -or $PullModel)) {
    Write-Host "
Financial Master - Ollama Model Manager
======================================

Usage: .\scripts\setup_ollama_models.ps1 [Options]

Options:
  -PullRecommended    Pull recommended models for Financial Master
  -PullAll           Pull all available models (50+ GB)
  -ListModels        List installed models
  -RemoveAll         Remove all installed models
  -PullModel <name>  Pull a specific model

Recommended Models:
" -ForegroundColor Blue
    
    foreach ($model in $RecommendedModels) {
        Write-Host "  • $($model.Name)" -ForegroundColor White
        Write-Host "    $($model.Description) - $($model.UseCase)"
    }
    
    Write-Host ""
}
