# PowerShell Script: Python Version Manager for Financial Master
# Shows available versions, installs latest, manages environments

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Python Version Manager - Financial Master" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check current Python installation
Write-Host "Current Python Installation:" -ForegroundColor Yellow
$currentPython = python --version 2>&1
Write-Host "  $currentPython" -ForegroundColor Green
Write-Host ""

# Check py launcher for available versions
Write-Host "Available Python Versions on Your System:" -ForegroundColor Yellow
Write-Host ""

$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher) {
    $versions = py --list 2>&1 | Where-Object { $_ -match "Python" }
    foreach ($version in $versions) {
        $isDefault = $version -match "\*"
        if ($isDefault) {
            Write-Host "  $version (CURRENT DEFAULT)" -ForegroundColor Green
        } else {
            Write-Host "  $version" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  py launcher not found - using system Python only" -ForegroundColor Yellow
}

Write-Host ""

# Function to show menu
function Show-Menu {
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  1. Install Latest Python (via Microsoft Store)" -ForegroundColor White
    Write-Host "  2. Switch to Python 3.13" -ForegroundColor White
    Write-Host "  3. Switch to Python 3.12" -ForegroundColor White
    Write-Host "  4. Switch to Python 3.11" -ForegroundColor White
    Write-Host "  5. Create Virtual Environment with Selected Python" -ForegroundColor White
    Write-Host "  6. Check Python Installation Details" -ForegroundColor White
    Write-Host "  7. Upgrade pip and tools" -ForegroundColor White
    Write-Host "  0. Exit" -ForegroundColor White
    Write-Host ""
}

function Install-LatestPython {
    Write-Host "Installing Python via Microsoft Store..." -ForegroundColor Yellow
    Write-Host "This will open Microsoft Store. Install Python 3.12 or 3.13" -ForegroundColor Yellow
    Start-Process "ms-windows-store://search/?query=python"
    Write-Host "After installation, run this script again to verify." -ForegroundColor Green
}

function Switch-Python {
    param([string]$version)
    Write-Host "Switching to Python $version..." -ForegroundColor Yellow
    
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $target = "-$version"
        $pythonPath = py $target -c "import sys; print(sys.executable)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python $version found at: $pythonPath" -ForegroundColor Green
            
            # Create alias for this session
            $aliasCmd = "function global:python$version { & py $target `$args }"
            Invoke-Expression $aliasCmd
            Write-Host "Alias 'python$version' created for this session" -ForegroundColor Green
            Write-Host "Use it like: python$version script.py" -ForegroundColor Gray
        } else {
            Write-Host "Python $version not found. Install via Microsoft Store?" -ForegroundColor Red
            $install = Read-Host "Open Microsoft Store to install Python $version? (y/n)"
            if ($install -eq 'y') {
                Install-LatestPython
            }
        }
    } else {
        Write-Host "py launcher not available. Cannot switch versions." -ForegroundColor Red
    }
}

function Create-Venv {
    Write-Host "Creating Virtual Environment..." -ForegroundColor Yellow
    $projectRoot = Get-Location
    $venvPath = Join-Path $projectRoot ".venv"
    
    if (Test-Path $venvPath) {
        $remove = Read-Host ".venv already exists. Remove and recreate? (y/n)"
        if ($remove -eq 'y') {
            Remove-Item -Recurse -Force $venvPath
        } else {
            Write-Host "Using existing .venv" -ForegroundColor Yellow
            return
        }
    }
    
    python -m venv $venvPath
    Write-Host "Virtual environment created at: $venvPath" -ForegroundColor Green
    
    # Install dependencies
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    $pipPath = Join-Path $venvPath "Scripts\pip.exe"
    & $pipPath install --upgrade pip
    
    $reqFile = Join-Path $projectRoot "requirements.txt"
    if (Test-Path $reqFile) {
        & $pipPath install -r $reqFile
        Write-Host "Dependencies installed!" -ForegroundColor Green
    }
}

function Check-PythonDetails {
    Write-Host "Python Installation Details:" -ForegroundColor Cyan
    Write-Host ""
    
    $pythonPath = python -c "import sys; print(sys.executable)" 2>&1
    Write-Host "Executable: $pythonPath" -ForegroundColor Gray
    
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>&1
    Write-Host "Version: $version" -ForegroundColor Gray
    
    $sitePackages = python -c "import site; print(site.getsitepackages()[0])" 2>&1
    Write-Host "Site Packages: $sitePackages" -ForegroundColor Gray
    
    $pipVersion = pip --version 2>&1
    Write-Host "pip: $pipVersion" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "Installed Packages (top 10):" -ForegroundColor Yellow
    pip list | Select-Object -First 12 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
}

function Upgrade-PipTools {
    Write-Host "Upgrading pip and essential tools..." -ForegroundColor Yellow
    python -m pip install --upgrade pip setuptools wheel
    pip install --upgrade pytest black flake8 mypy isort
    Write-Host "Tools upgraded!" -ForegroundColor Green
}

# Main menu loop
while ($true) {
    Show-Menu
    $choice = Read-Host "Select option (0-7)"
    
    switch ($choice) {
        '1' { Install-LatestPython }
        '2' { Switch-Python "3.13" }
        '3' { Switch-Python "3.12" }
        '4' { Switch-Python "3.11" }
        '5' { Create-Venv }
        '6' { Check-PythonDetails }
        '7' { Upgrade-PipTools }
        '0' { 
            Write-Host "Exiting..." -ForegroundColor Green
            exit 0 
        }
        default { 
            Write-Host "Invalid option. Please try again." -ForegroundColor Red 
        }
    }
    
    Write-Host ""
    Read-Host "Press Enter to continue"
    Clear-Host
}
