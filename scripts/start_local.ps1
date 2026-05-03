# Start Financial Master Locally
# One-click launcher for beginners

$ErrorActionPreference = "Stop"

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-Status($Message, $Color = "White") {
    Write-Host $Message -ForegroundColor $Color
}

# Find project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Status @"
╔══════════════════════════════════════════════════════════════════════╗
║              STARTING FINANCIAL MASTER (LOCAL MODE)                  ║
╚══════════════════════════════════════════════════════════════════════╝
" $Cyan

# Check if virtual environment exists
$VenvPath = Join-Path $ProjectRoot ".venv"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

if (-not (Test-Path $ActivateScript)) {
    Write-Status "❌ Virtual environment not found!" $Red
    Write-Status "Please run: .\scripts\complete_setup.ps1 first" $Yellow
    exit 1
}

# Activate virtual environment
Write-Status "🌐 Activating virtual environment..." $Cyan
& $ActivateScript

# Check if .env exists
$EnvFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Status "⚠️  .env file not found! Creating from template..." $Yellow
    $EnvExample = Join-Path $ProjectRoot ".env.example"
    if (Test-Path $EnvExample) {
        Copy-Item $EnvExample $EnvFile
        Write-Status "✅ .env file created. Please add your API keys!" $Green
    }
}

# Check API keys
Write-Status "🔑 Checking API configuration..." $Cyan
$EnvContent = Get-Content $EnvFile -Raw
$MissingKeys = @()

if ($EnvContent -match "ALPACA_API_KEY=your_alpaca_key_here|ALPACA_API_KEY=") {
    $MissingKeys += "ALPACA_API_KEY"
}
if ($EnvContent -match "POLYGON_API_KEY=your_polygon_key_here|POLYGON_API_KEY=") {
    $MissingKeys += "POLYGON_API_KEY"
}

if ($MissingKeys.Count -gt 0) {
    Write-Status "⚠️  Missing API keys: $($MissingKeys -join ', ')" $Yellow
    Write-Status "You can still start, but trading features won't work." $Yellow
    Write-Status "Edit $EnvFile to add your free API keys." $Yellow
    $Continue = Read-Host "Continue anyway? (y/n) [default: y]"
    if ($Continue -eq "n") {
        exit 0
    }
}

# Start the application
Write-Status "🚀 Starting Financial Master..." $Green
Write-Status "URL: http://localhost:8000" $Cyan
Write-Status "API Docs: http://localhost:8000/docs" $Cyan
Write-Status "Press Ctrl+C to stop" $Yellow

# Change to project root
Set-Location $ProjectRoot

# Start the application
try {
    $AppScript = Join-Path $ProjectRoot "src\backend\app\main.py"
    if (Test-Path $AppScript) {
        python -m uvicorn src.backend.app.main:app --host 0.0.0.0 --port 8000 --reload
    } else {
        Write-Status "⚠️  Main application not found at expected location" $Yellow
        Write-Status "Looking for alternative entry points..." $Yellow
        
        # Try alternative locations
        $AltPaths = @(
            "src\backend\main.py",
            "app\main.py",
            "main.py"
        )
        
        $Found = $false
        foreach ($Path in $AltPaths) {
            $FullPath = Join-Path $ProjectRoot $Path
            if (Test-Path $FullPath) {
                Write-Status "✅ Found: $Path" $Green
                python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
                $Found = $true
                break
            }
        }
        
        if (-not $Found) {
            Write-Status "❌ Could not find application entry point" $Red
            Write-Status "Please check your project structure" $Red
        }
    }
} catch {
    Write-Status "❌ Error starting application: $_" $Red
    Write-Status "Check that all dependencies are installed: pip install -r requirements.txt" $Yellow
}
