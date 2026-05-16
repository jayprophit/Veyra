# Deploy Veyra to Kubernetes
# Usage: .\scripts\k8s-deploy.ps1

param(
    [string]$Namespace = "default",
    [switch]$Watch = $false
)

$ErrorActionPreference = "Stop"

Write-Host "☸️  Deploying Veyra to Kubernetes (namespace: $Namespace)..." -ForegroundColor Cyan

try {
    # Create namespace if it doesn't exist
    & kubectl create namespace $Namespace --dry-run=client -o yaml | & kubectl apply -f -
    
    # Apply Kustomization
    Write-Host "📦 Applying Kubernetes manifests..." -ForegroundColor Yellow
    & kubectl apply -k infrastructure/kubernetes/ -n $Namespace
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Kubernetes deployment applied successfully" -ForegroundColor Green
        
        Write-Host "`n🔍 Checking deployment status..." -ForegroundColor Yellow
        & kubectl get deployments -n $Namespace
        & kubectl get services -n $Namespace
        & kubectl get pods -n $Namespace
        
        if ($Watch) {
            Write-Host "`n👀 Watching pod status (Ctrl+C to exit)..." -ForegroundColor Cyan
            & kubectl get pods -n $Namespace -w
        }
    } else {
        Write-Host "❌ Kubernetes deployment failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
