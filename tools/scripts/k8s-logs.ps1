# View Kubernetes pod logs
# Usage: .\scripts\k8s-logs.ps1 [-Pod "pod-name"] [-Namespace "default"] [-Follow]

param(
    [string]$Pod = "veyra-app",
    [string]$Namespace = "default",
    [switch]$Follow = $false
)

$ErrorActionPreference = "Stop"

Write-Host "📋 Fetching logs for pod: $Pod (namespace: $Namespace)" -ForegroundColor Cyan

try {
    $logsArgs = @("logs", $Pod, "-n", $Namespace)
    
    if ($Follow) {
        $logsArgs += "-f"
    }
    
    & kubectl @logsArgs
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
