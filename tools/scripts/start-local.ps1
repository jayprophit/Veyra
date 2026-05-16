param(
    [int]$ApiPort = 8000,
    [int]$WebPort = 3000,
    [string]$Model = "llama3.2:3b",
    [switch]$SkipOllamaStart
)

$ErrorActionPreference = "Stop"

function Require-Command([string]$Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) {
        throw "Required command not found on PATH: $Name"
    }
    return $command
}

function Test-Http([string]$Url) {
    try {
        Invoke-RestMethod -Uri $Url -TimeoutSec 5 | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Test-PortAvailable([int]$Port) {
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return -not $listener
}

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

function Stop-StartedProcess($Process) {
    if ($Process -and -not $Process.HasExited) {
        Stop-ProcessTree $Process.Id
    }
}

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$dataDir = Join-Path $root "data"
$logDir = Join-Path $dataDir "logs"
$runtimeDir = Join-Path $dataDir "runtime"
$stateFile = Join-Path $runtimeDir "local-state.json"
$dbPath = Join-Path $dataDir "veyra_local.db"

New-Item -ItemType Directory -Force -Path $dataDir, $logDir, $runtimeDir | Out-Null

$python = Require-Command "python"
$pnpm = Get-Command "pnpm.cmd" -ErrorAction SilentlyContinue
if (-not $pnpm) {
    $pnpm = Require-Command "pnpm"
}

$env:DATABASE_URL = "sqlite+pysqlite:///$($dbPath.Replace('\', '/'))"
if (-not $env:OLLAMA_HOST) {
    $env:OLLAMA_HOST = "http://127.0.0.1:11434"
}
$env:AI_MODEL = $Model
if (-not $env:OLLAMA_CHAT_TIMEOUT_SECONDS) {
    $env:OLLAMA_CHAT_TIMEOUT_SECONDS = "420"
}
$env:VEYRA_CORS_ORIGINS = "http://localhost:$WebPort,http://127.0.0.1:$WebPort"

if (Test-Path $stateFile) {
    Write-Host "Existing local runtime state found. Run pnpm local:stop before starting again." -ForegroundColor Yellow
    exit 1
}

foreach ($port in @($ApiPort, $WebPort)) {
    if (-not (Test-PortAvailable $port)) {
        throw "Port $port is already in use. Stop the existing service or choose another port."
    }
}

$apiLog = Join-Path $logDir "api.stdout.log"
$apiErrorLog = Join-Path $logDir "api.stderr.log"
$webLog = Join-Path $logDir "web.stdout.log"
$webErrorLog = Join-Path $logDir "web.stderr.log"
$ollamaLog = Join-Path $logDir "ollama.stdout.log"
$ollamaErrorLog = Join-Path $logDir "ollama.stderr.log"

$ollamaReady = Test-Http "$($env:OLLAMA_HOST)/api/version"
$ollamaProcess = $null
$ollamaStartedByVeyra = $false
if (-not $ollamaReady -and -not $SkipOllamaStart) {
    $ollama = Get-Command "ollama.exe" -ErrorAction SilentlyContinue
    if ($ollama) {
        $ollamaProcess = Start-Process `
            -FilePath $ollama.Source `
            -ArgumentList @("serve") `
            -WindowStyle Hidden `
            -RedirectStandardOutput $ollamaLog `
            -RedirectStandardError $ollamaErrorLog `
            -PassThru
        $ollamaStartedByVeyra = $true

        for ($attempt = 0; $attempt -lt 20; $attempt++) {
            Start-Sleep -Seconds 1
            if (Test-Http "$($env:OLLAMA_HOST)/api/version") {
                $ollamaReady = $true
                break
            }
        }
    }
}

$apiProcess = Start-Process `
    -FilePath $python.Source `
    -ArgumentList @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "$ApiPort") `
    -WorkingDirectory (Join-Path $root "services\api-gateway") `
    -WindowStyle Hidden `
    -RedirectStandardOutput $apiLog `
    -RedirectStandardError $apiErrorLog `
    -PassThru

$webProcess = Start-Process `
    -FilePath $pnpm.Source `
    -ArgumentList @("--filter", "@veyra/web", "exec", "vite", "--host", "127.0.0.1", "--port", "$WebPort") `
    -WorkingDirectory $root `
    -WindowStyle Hidden `
    -RedirectStandardOutput $webLog `
    -RedirectStandardError $webErrorLog `
    -PassThru

$state = [ordered]@{
    started_at = (Get-Date).ToUniversalTime().ToString("o")
    api_pid = $apiProcess.Id
    web_pid = $webProcess.Id
    api_port = $ApiPort
    web_port = $WebPort
    database_url = $env:DATABASE_URL
    ollama_host = $env:OLLAMA_HOST
    ai_model = $env:AI_MODEL
    ollama_pid = if ($ollamaProcess) { $ollamaProcess.Id } else { $null }
    ollama_started_by_veyra = $ollamaStartedByVeyra
}
$state | ConvertTo-Json | Set-Content -Path $stateFile -Encoding UTF8

$apiReady = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Seconds 1
    if (Test-Http "http://127.0.0.1:$ApiPort/health") {
        $apiReady = $true
        break
    }
}

if (-not $apiReady) {
    Stop-StartedProcess $apiProcess
    Stop-StartedProcess $webProcess
    if ($ollamaStartedByVeyra) {
        Stop-StartedProcess $ollamaProcess
    }
    Remove-Item -LiteralPath $stateFile -Force -ErrorAction SilentlyContinue
    Write-Host "API did not become healthy. Check $apiLog" -ForegroundColor Red
    exit 1
}

$webReady = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Seconds 1
    if (Test-Http "http://127.0.0.1:$WebPort") {
        $webReady = $true
        break
    }
}

if (-not $webReady) {
    Stop-StartedProcess $apiProcess
    Stop-StartedProcess $webProcess
    if ($ollamaStartedByVeyra) {
        Stop-StartedProcess $ollamaProcess
    }
    Remove-Item -LiteralPath $stateFile -Force -ErrorAction SilentlyContinue
    Write-Host "Web app did not become healthy. Check $webLog" -ForegroundColor Red
    exit 1
}

Write-Host "Veyra local runtime started." -ForegroundColor Green
Write-Host "Web:    http://127.0.0.1:$WebPort"
Write-Host "API:    http://127.0.0.1:$ApiPort"
Write-Host "Data:   $dbPath"
Write-Host "Ollama: $($env:OLLAMA_HOST) [$(if ($ollamaReady) { 'available' } else { 'not reachable' })]"
Write-Host "Logs:   $logDir"
