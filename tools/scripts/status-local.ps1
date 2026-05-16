$ErrorActionPreference = "Stop"

function Test-Endpoint([string]$Url) {
    try {
        return Invoke-RestMethod -Uri $Url -TimeoutSec 10
    } catch {
        return $null
    }
}

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$stateFile = Join-Path $root "data\runtime\local-state.json"

if (-not (Test-Path $stateFile)) {
    Write-Host "Local runtime is not started."
    exit 1
}

$state = Get-Content -Raw $stateFile | ConvertFrom-Json
$api = Test-Endpoint "http://127.0.0.1:$($state.api_port)/health"
$ollama = Test-Endpoint "$($state.ollama_host)/api/version"

Write-Host "Veyra local runtime"
Write-Host "Started: $($state.started_at)"
Write-Host "Web PID: $($state.web_pid)"
Write-Host "API PID: $($state.api_pid)"
Write-Host "API:     $([bool]$api)"
Write-Host "Ollama:  $([bool]$ollama)"
Write-Host "Managed: $($state.ollama_started_by_veyra)"
Write-Host "Model:   $($state.ai_model)"
Write-Host "Data:    $($state.database_url)"
