$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$stateFile = Join-Path $root "data\runtime\local-state.json"

function Stop-ProcessTree([int]$ProcessId) {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $ProcessId" -ErrorAction SilentlyContinue
    foreach ($child in $children) {
        Stop-ProcessTree $child.ProcessId
    }

    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
    }
}

if (-not (Test-Path $stateFile)) {
    Write-Host "No local runtime state found."
    exit 0
}

$state = Get-Content -Raw $stateFile | ConvertFrom-Json
foreach ($pidValue in @($state.api_pid, $state.web_pid)) {
    Stop-ProcessTree $pidValue
}

if ($state.ollama_started_by_veyra -and $state.ollama_pid) {
    Stop-ProcessTree $state.ollama_pid
}

Remove-Item -LiteralPath $stateFile -Force
Write-Host "Veyra local runtime stopped." -ForegroundColor Green
