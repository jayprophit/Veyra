# Veyra - Health Check
# Quick diagnostic script for troubleshooting

$ErrorActionPreference = "Continue"

$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-Status($Message, $Color = "White") {
    Write-Host $Message -ForegroundColor $Color
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "
╔══════════════════════════════════════════════════════════════════════╗
║                    SYSTEM HEALTH CHECK                               ║
╚══════════════════════════════════════════════════════════════════════╝
" -ForegroundColor $Cyan

$Issues = 0
$Warnings = 0

# Check 1: Python
Write-Status "`n1. Checking Python..." $Cyan
try {
    $PyVersion = python --version 2>&1
    Write-Status "   ✅ $PyVersion" $Green
}
catch {
    Write-Status "   ❌ Python not found in PATH" $Red
    $Issues++
}

# Check 2: Virtual Environment
Write-Status "`n2. Checking Virtual Environment..." $Cyan
$VenvPath = Join-Path $ProjectRoot ".venv"
if (Test-Path $VenvPath) {
    Write-Status "   ✅ Virtual environment exists" $Green
    $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (Test-Path $ActivateScript) {
        Write-Status "   ✅ Activation script found" $Green
    }
    else {
        Write-Status "   ❌ Activation script missing" $Red
        $Issues++
    }
}
else {
    Write-Status "   ❌ Virtual environment not found" $Red
    Write-Status "   Run: .\scripts\complete_setup.ps1" $Yellow
    $Issues++
}

# Check 3: Git
Write-Status "`n3. Checking Git..." $Cyan
try {
    $GitVersion = git --version 2>&1
    Write-Status "   ✅ $GitVersion" $Green
}
catch {
    Write-Status "   ❌ Git not found" $Red
    $Issues++
}

# Check 4: Environment File
Write-Status "`n4. Checking Environment File..." $Cyan
$EnvFile = Join-Path $ProjectRoot ".env"
if (Test-Path $EnvFile) {
    Write-Status "   ✅ .env file exists" $Green
    $EnvContent = Get-Content $EnvFile -Raw
    
    # Check for placeholder keys
    $Placeholders = @()
    if ($EnvContent -match "your_alpaca_key_here") { $Placeholders += "ALPACA_API_KEY" }
    if ($EnvContent -match "your_alpaca_secret_here") { $Placeholders += "ALPACA_SECRET_KEY" }
    if ($Placeholders.Count -gt 0) {
        Write-Status "   ⚠️  Placeholder API keys detected: $($Placeholders -join ', ')" $Yellow
        Write-Status "   Edit .env and add real API keys" $Yellow
        $Warnings++
    }
    else {
        Write-Status "   ✅ API keys configured" $Green
    }
}
else {
    Write-Status "   ❌ .env file not found" $Red
    Write-Status "   Run: .\scripts\complete_setup.ps1" $Yellow
    $Issues++
}

# Check 5: Dependencies
Write-Status "`n5. Checking Python Dependencies..." $Cyan
try {
    python -c "import fastapi, uvicorn, pandas, sqlalchemy, alpaca_trade_api, requests" 2>&1 | Out-Null
    Write-Status "   ✅ Core dependencies installed" $Green
}
catch {
    Write-Status "   ❌ Some dependencies missing" $Red
    Write-Status "   Run: pip install -r requirements.txt" $Yellow
    $Issues++
}

# Check 6: Project Structure
Write-Status "`n6. Checking Project Structure..." $Cyan
$RequiredDirs = @("src", "tests", "docs", "scripts")
foreach ($Dir in $RequiredDirs) {
    $DirPath = Join-Path $ProjectRoot $Dir
    if (Test-Path $DirPath) {
        Write-Status "   ✅ $Dir/ directory exists" $Green
    }
    else {
        Write-Status "   ⚠️  $Dir/ directory not found" $Yellow
        $Warnings++
    }
}

# Check 7: Application Entry Point
Write-Status "`n7. Checking Application Files..." $Cyan
$EntryPoints = @(
    "src\backend\app\main.py",
    "src\backend\main.py",
    "app\main.py"
)
$Found = $false
foreach ($Path in $EntryPoints) {
    $FullPath = Join-Path $ProjectRoot $Path
    if (Test-Path $FullPath) {
        Write-Status "   ✅ Found entry point: $Path" $Green
        $Found = $true
        break
    }
}
if (-not $Found) {
    Write-Status "   ❌ No application entry point found" $Red
    $Issues++
}

# Summary
Write-Status "`n══════════════════════════════════════════════════════════════════" $Cyan
if ($Issues -eq 0 -and $Warnings -eq 0) {
    Write-Status "✅ ALL CHECKS PASSED! System is ready." $Green
}
elseif ($Issues -eq 0) {
    Write-Status "✅ System functional with $Warnings warnings" $Yellow
}
else {
    Write-Status "❌ Found $Issues issue(s) and $Warnings warning(s)" $Red
}

Write-Status "`nQuick Fixes:" $Cyan
Write-Status "  • Run setup:        .\scripts\complete_setup.ps1" $Yellow
Write-Status "  • Start app:        .\scripts\start_local.ps1" $Yellow
Write-Status "  • Check docs:       .\docs\BEGINNERS_GUIDE.md" $Yellow
Write-Status "  • API setup:        .\docs\compliance\API_SETUP_GUIDE.md" $Yellow

Write-Status "`n" $Cyan
