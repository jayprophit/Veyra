# ================================================================================
# Financial Master - Repository Cloning Script
# Clones all open-source dependencies for IP ownership
# Run as Administrator
# ================================================================================

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Configuration
$BASE_DIR = "C:\Users\jpowe\Desktop\Financial Master\08_Repositories"
$REPOSITORIES = @(
    # Core Infrastructure
    @{ Name = "ghostfolio"; URL = "https://github.com/ghostfolio/ghostfolio.git"; Branch = "main"; Description = "Portfolio tracking UI reference" },
    @{ Name = "firefly-iii"; URL = "https://github.com/firefly-iii/firefly-iii.git"; Branch = "main"; Description = "Budgeting engine" },
    @{ Name = "actual"; URL = "https://github.com/actualbudget/actual.git"; Branch = "main"; Description = "Zero-based budgeting" },
    @{ Name = "ccxt"; URL = "https://github.com/ccxt/ccxt.git"; Branch = "master"; Description = "Multi-exchange trading abstraction" },
    @{ Name = "freqtrade"; URL = "https://github.com/freqtrade/freqtrade.git"; Branch = "stable"; Description = "Trading bot framework" },
    @{ Name = "huginn"; URL = "https://github.com/huginn/huginn.git"; Branch = "master"; Description = "Agent orchestration" },
    
    # AI/ML Infrastructure
    @{ Name = "langchain"; URL = "https://github.com/langchain-ai/langchain.git"; Branch = "master"; Description = "LLM framework" },
    @{ Name = "chroma"; URL = "https://github.com/chroma-core/chroma.git"; Branch = "main"; Description = "Vector database for RAG" },
    @{ Name = "open-webui"; URL = "https://github.com/open-webui/open-webui.git"; Branch = "main"; Description = "LLM Web UI" },
    
    # Backend Infrastructure
    @{ Name = "supabase"; URL = "https://github.com/supabase/supabase.git"; Branch = "master"; Description = "Backend-as-a-Service" },
    @{ Name = "nocodb"; URL = "https://github.com/nocodb/nocodb.git"; Branch = "main"; Description = "Database GUI" },
    @{ Name = "directus"; URL = "https://github.com/directus/directus.git"; Branch = "main"; Description = "Headless CMS/API" },
    
    # Dashboard/Frontend Reference
    @{ Name = "maybe"; URL = "https://github.com/maybe-finance/maybe.git"; Branch = "main"; Description = "Financial planning app" },
    @{ Name = "plane"; URL = "https://github.com/makeplane/plane.git"; Branch = "main"; Description = "Project management" },
    @{ Name = "tooljet"; URL = "https://github.com/ToolJet/ToolJet.git"; Branch = "main"; Description = "Low-code dashboard" },
    @{ Name = "apitable"; URL = "https://github.com/apitable/apitable.git"; Branch = "develop"; Description = "Database + API + UI" },
    @{ Name = "dashpress"; URL = "https://github.com/dashpressHQ/dashpress.git"; Branch = "main"; Description = "Admin dashboard" },
    
    # Database & Cache
    @{ Name = "postgres"; URL = "https://github.com/postgres/postgres.git"; Branch = "master"; Description = "PostgreSQL reference" },
    @{ Name = "redis"; URL = "https://github.com/redis/redis.git"; Branch = "unstable"; Description = "Cache/Queue" },
    
    # Monitoring & Observability
    @{ Name = "grafana"; URL = "https://github.com/grafana/grafana.git"; Branch = "main"; Description = "Metrics visualization" },
    @{ Name = "prometheus"; URL = "https://github.com/prometheus/prometheus.git"; Branch = "main"; Description = "Metrics collection" },
    
    # Security
    @{ Name = "vault"; URL = "https://github.com/hashicorp/vault.git"; Branch = "main"; Description = "Secret management" },
    
    # Additional Financial Tools
    @{ Name = "firefly-iii-data-importer"; URL = "https://github.com/firefly-iii/data-importer.git"; Branch = "main"; Description = "Bank import tool" },
    @{ Name = "homebank-converter"; URL = "https://github.com/BenjaminDebeerst/homebank-converter.git"; Branch = "master"; Description = "Statement converter" },
    @{ Name = "gnucash"; URL = "https://github.com/Gnucash/gnucash.git"; Branch = "stable"; Description = "Accounting software" }
)

# Create base directory
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Financial Master - Repository Cloning Script" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

if (!(Test-Path $BASE_DIR)) {
    New-Item -ItemType Directory -Path $BASE_DIR -Force | Out-Null
    Write-Host "✓ Created directory: $BASE_DIR" -ForegroundColor Green
} else {
    Write-Host "✓ Directory exists: $BASE_DIR" -ForegroundColor Yellow
}

Set-Location $BASE_DIR

# Statistics
$successCount = 0
$failCount = 0
$skipCount = 0

# Clone each repository
foreach ($repo in $REPOSITORIES) {
    $repoName = $repo.Name
    $repoUrl = $repo.URL
    $branch = $repo.Branch
    $description = $repo.Description
    
    Write-Host ""
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Gray
    Write-Host "Cloning: $repoName" -ForegroundColor White
    Write-Host "Description: $description" -ForegroundColor DarkGray
    Write-Host "URL: $repoUrl" -ForegroundColor DarkGray
    Write-Host "Branch: $branch" -ForegroundColor DarkGray
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Gray
    
    if (Test-Path $repoName) {
        Write-Host "⚠ Repository already exists: $repoName" -ForegroundColor Yellow
        
        # Update existing repository
        try {
            Set-Location $repoName
            Write-Host "  Updating repository..." -ForegroundColor DarkGray
            
            git fetch origin
            git checkout $branch
            git pull origin $branch
            
            Set-Location ..
            $skipCount++
            Write-Host "✓ Updated: $repoName" -ForegroundColor Green
        }
        catch {
            Write-Host "✗ Failed to update: $repoName - $($_.Exception.Message)" -ForegroundColor Red
            Set-Location ..
            $failCount++
        }
    }
    else {
        # Clone new repository
        try {
            Write-Host "  Cloning repository..." -ForegroundColor DarkGray
            
            git clone --depth 1 --branch $branch $repoUrl $repoName 2>&1 | Out-Null
            
            if (Test-Path $repoName) {
                $successCount++
                Write-Host "✓ Cloned: $repoName" -ForegroundColor Green
                
                # Create README for this repo
                $readmeContent = @"
# $repoName

**Source:** $repoUrl  
**Branch:** $branch  
**Description:** $description  

**Cloned for:** Financial Master System 5★ Implementation  
**Purpose:** Reference implementation / Fork base for customization  
**License:** Check original repository for license terms  

## Notes

This repository was cloned as part of the Financial Master System build-out
to ensure full IP ownership and customization capability.

## Integration Points

- [ ] Identify useful components
- [ ] Extract/fork relevant code
- [ ] Customize for Financial Master requirements
- [ ] Document modifications

---
**Cloned:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
                $readmeContent | Out-File -FilePath "$repoName\FINANCIAL_MASTER_NOTES.md" -Encoding UTF8
            }
            else {
                $failCount++
                Write-Host "✗ Failed to clone: $repoName (directory not created)" -ForegroundColor Red
            }
        }
        catch {
            $failCount++
            Write-Host "✗ Failed to clone: $repoName - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Create master index
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Creating Master Index..." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$indexContent = @"
# Financial Master - Repository Index

**Total Repositories:** $($REPOSITORIES.Count)  
**Successfully Cloned:** $successCount  
**Updated:** $skipCount  
**Failed:** $failCount  
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Core Infrastructure

| Repository | Branch | Purpose | Status |
|------------|--------|---------|--------|
"@

foreach ($repo in $REPOSITORIES) {
    $status = if (Test-Path $repo.Name) { "✅ Ready" } else { "❌ Missing" }
    $indexContent += "| $($repo.Name) | $($repo.Branch) | $($repo.Description) | $status |`n"
}

$indexContent += @"

## Usage

### Update All Repositories
```powershell
cd "$BASE_DIR"
.\CLONE_ALL_REPOSITORIES.ps1
```

### Individual Repository
```powershell
cd "$BASE_DIR\ghostfolio"
git pull origin main
```

## Next Steps

1. Review each repository's `FINANCIAL_MASTER_NOTES.md`
2. Identify components to extract/fork
3. Document integration points
4. Build custom implementations

## IP Ownership Note

All repositories are open-source and cloned for:
- Reference implementation study
- Component extraction and customization
- Ensuring no external dependencies for core functionality

Respect original licenses when forking/modifying.

---
**Financial Master System v5.0 Implementation**
"@

$indexContent | Out-File -FilePath "$BASE_DIR\REPOSITORY_INDEX.md" -Encoding UTF8
Write-Host "✓ Created REPOSITORY_INDEX.md" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "CLONING COMPLETE" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Statistics:" -ForegroundColor White
Write-Host "  ✅ Successfully cloned: $successCount" -ForegroundColor Green
Write-Host "  ⚠ Updated: $skipCount" -ForegroundColor Yellow
Write-Host "  ❌ Failed: $failCount" -ForegroundColor Red
Write-Host "  📦 Total repositories: $($REPOSITORIES.Count)" -ForegroundColor White
Write-Host ""
Write-Host "Location: $BASE_DIR" -ForegroundColor Cyan
Write-Host "Index file: $BASE_DIR\REPOSITORY_INDEX.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Review REPOSITORY_INDEX.md" -ForegroundColor Gray
Write-Host "  2. Explore each repository" -ForegroundColor Gray
Write-Host "  3. Identify components to integrate" -ForegroundColor Gray
Write-Host "  4. Run setup scripts in 00_Master_Spreadsheet_System" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan

# Keep window open
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
