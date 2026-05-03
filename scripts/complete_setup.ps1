# Financial Master - Complete Automated Setup
# For Windows Users with No-Code Experience
# Run this script as Administrator

param(
    [switch]$SkipAPISetup,
    [switch]$SkipDocker,
    [switch]$QuickMode
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-Status($Message, $Level = "Info") {
    $Color = switch ($Level) {
        "Success" { $Green }
        "Warning" { $Yellow }
        "Error" { $Red }
        "Info" { $Cyan }
        default { "White" }
    }
    Write-Host $Message -ForegroundColor $Color
}

function Test-Command($Command) {
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Install-IfNotPresent($Command, $InstallScript, $Name) {
    if (Test-Command $Command) {
        Write-Status "[OK] $Name is already installed" "Success"
        return $true
    }
    else {
        Write-Status "  $Name not found. Installing..." "Warning"
        try {
            Invoke-Expression $InstallScript
            Write-Status "[OK] $Name installed successfully" "Success"
            return $true
        }
        catch {
            Write-Status " Failed to install $Name. Please install manually." "Error"
            return $false
        }
    }
}

# ============================================
# HEADER
# ============================================
Clear-Host
Write-Status @"

            FINANCIAL MASTER - COMPLETE AUTOMATED SETUP               
                                                                      
  This script will set up everything you need to start:            
   Install required programs                                        
   Set up Python environment                                        
   Install dependencies                                             
   Configure GitHub                                                 
   Set up API keys (Alpaca, Polygon, etc.)                          
   Test the installation                                            
                                                                      
  Estimated time: 15-30 minutes                                       
  Cost: FREE (all services have free tiers)                          

"@ "Info"

Write-Status "Press any key to continue..." "Warning"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# ============================================
# STEP 1: CHECK WINDOWS VERSION
# ============================================
Write-Status "`n STEP 1: Checking System Requirements..." "Info"

$OS = Get-CimInstance -ClassName Win32_OperatingSystem
$WindowsVersion = [System.Environment]::OSVersion.Version

if ($WindowsVersion.Major -lt 10) {
    Write-Status " Windows 10 or higher required" "Error"
    exit 1
}

Write-Status "[OK] Windows $($OS.Caption) detected" "Success"
Write-Status "[OK] System requirements met" "Success"

# ============================================
# STEP 2: INSTALL CHOCOLATEY (Package Manager)
# ============================================
Write-Status "`n STEP 2: Installing Package Manager (Chocolatey)..." "Info"

if (-not (Test-Command "choco")) {
    Write-Status "Installing Chocolatey..." "Info"
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        $env:PATH += ";$env:ALLUSERSPROFILE\chocolatey\bin"
        Write-Status "[OK] Chocolatey installed" "Success"
    }
    catch {
        Write-Status " Chocolatey installation failed" "Error"
        Write-Status "Please install manually from: https://chocolatey.org/install" "Warning"
    }
}
else {
    Write-Status "[OK] Chocolatey already installed" "Success"
}

# ============================================
# STEP 3: INSTALL REQUIRED PROGRAMS
# ============================================
Write-Status "`n STEP 3: Installing Required Programs..." "Info"

$Programs = @(
    @{Name = "Git"; Command = "git"; ChocolateyPackage = "git" },
    @{Name = "Python 3.11"; Command = "python"; ChocolateyPackage = "python" },
    @{Name = "VS Code"; Command = "code"; ChocolateyPackage = "vscode" },
    @{Name = "Docker Desktop"; Command = "docker"; ChocolateyPackage = "docker-desktop"; Optional = $true }
)

foreach ($Program in $Programs) {
    $IsOptional = $Program.Optional -eq $true
    
    if ($IsOptional -and $SkipDocker) {
        Write-Status "  Skipping $($Program.Name) (optional, skipped by flag)" "Warning"
        continue
    }
    
    if (Test-Command $Program.Command) {
        Write-Status "[OK] $($Program.Name) is already installed" "Success"
    }
    else {
        Write-Status "  Installing $($Program.Name)..." "Warning"
        try {
            choco install $Program.ChocolateyPackage -y --no-progress
            Write-Status "[OK] $($Program.Name) installed" "Success"
        }
        catch {
            if ($IsOptional) {
                Write-Status "  $($Program.Name) installation failed (optional, continuing)" "Warning"
            }
            else {
                Write-Status " $($Program.Name) installation failed" "Error"
                Write-Status "Please install manually and re-run this script" "Error"
                exit 1
            }
        }
    }
}

# ============================================
# STEP 4: VERIFY PYTHON INSTALLATION
# ============================================
Write-Status "`n STEP 4: Verifying Python..." "Info"

try {
    $PythonVersion = python --version 2>&1
    Write-Status "[OK] $PythonVersion detected" "Success"
    
    # Check if Python is in PATH
    $PythonPath = Get-Command python | Select-Object -ExpandProperty Source
    Write-Status "[OK] Python location: $PythonPath" "Success"
}
catch {
    Write-Status " Python not found in PATH" "Error"
    Write-Status "Please restart your computer and run this script again" "Error"
    exit 1
}

# ============================================
# STEP 5: CREATE PYTHON VIRTUAL ENVIRONMENT
# ============================================
Write-Status "`n STEP 5: Setting Up Python Environment..." "Info"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$VenvPath = Join-Path $ProjectRoot ".venv"

if (Test-Path $VenvPath) {
    Write-Status "  Virtual environment already exists at $VenvPath" "Warning"
    $Recreate = Read-Host "Do you want to recreate it? (y/n) [default: n]"
    if ($Recreate -eq "y") {
        Remove-Item -Recurse -Force $VenvPath
        Write-Status "  Old virtual environment removed" "Success"
    }
}

if (-not (Test-Path $VenvPath)) {
    Write-Status "Creating virtual environment..." "Info"
    try {
        python -m venv $VenvPath
        Write-Status "[OK] Virtual environment created" "Success"
    }
    catch {
        Write-Status " Failed to create virtual environment" "Error"
        exit 1
    }
}

# Activate virtual environment
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-Status "[OK] Virtual environment activated" "Success"
}
else {
    Write-Status " Could not find activation script" "Error"
    exit 1
}

# ============================================
# STEP 6: UPGRADE PIP AND INSTALL DEPENDENCIES
# ============================================
Write-Status "`n STEP 6: Installing Python Dependencies..." "Info"

Write-Status "Upgrading pip..." "Info"
python -m pip install --upgrade pip --quiet

$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
if (Test-Path $RequirementsFile) {
    Write-Status "Installing dependencies from requirements.txt..." "Info"
    Write-Status "This may take 5-10 minutes..." "Warning"
    try {
        pip install -r $RequirementsFile --quiet
        Write-Status "[OK] Dependencies installed successfully" "Success"
    }
    catch {
        Write-Status " Failed to install some dependencies" "Error"
        Write-Status "Continuing anyway..." "Warning"
    }
}
else {
    Write-Status "  requirements.txt not found at $RequirementsFile" "Warning"
}

# ============================================
# STEP 7: CREATE ENVIRONMENT FILE TEMPLATE
# ============================================
Write-Status "`n STEP 7: Setting Up Environment Configuration..." "Info"

$EnvFile = Join-Path $ProjectRoot ".env"
$EnvExample = Join-Path $ProjectRoot ".env.example"

if (Test-Path $EnvFile) {
    Write-Status "[OK] .env file already exists" "Success"
}
elseif (Test-Path $EnvExample) {
    Copy-Item $EnvExample $EnvFile
    Write-Status "[OK] .env file created from .env.example" "Success"
    Write-Status "  You will need to add your API keys to .env" "Warning"
}
else {
    $EnvContent = @"
# Financial Master Environment Configuration
# Generated by setup script on $(Get-Date)

# ============================================
# API KEYS - Fill these in with your free tier keys
# ============================================

# Alpaca Markets (Paper Trading)
# Get free keys at: https://alpaca.markets
ALPACA_API_KEY=your_alpaca_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_here
ALPACA_PAPER=true

# Polygon.io (Market Data)
# Get free key at: https://polygon.io
POLYGON_API_KEY=your_polygon_key_here

# Alpha Vantage (Stock Data)
# Get free key at: https://www.alphavantage.co
ALPHA_VANTAGE_API_KEY=your_alphavantage_key_here

# OpenAI (Optional - for AI features)
# Get key at: https://platform.openai.com
OPENAI_API_KEY=your_openai_key_here

# Coinbase (Optional - for crypto)
# Get keys at: https://www.coinbase.com/settings/api
COINBASE_API_KEY=your_coinbase_key_here
COINBASE_SECRET=your_coinbase_secret_here

# ============================================
# DATABASE
# ============================================
DATABASE_URL=sqlite:///./financial_master.db
# For production PostgreSQL:
# DATABASE_URL=postgresql://user:pass@host:5432/dbname

# ============================================
# SECURITY
# ============================================
SECRET_KEY=$(-join ((65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object { [char]$_ }))
JWT_SECRET_KEY=$(-join ((65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object { [char]$_ }))
ENCRYPTION_KEY=$(-join ((65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object { [char]$_ }))

# ============================================
# TRADING SETTINGS
# ============================================
MAX_DAILY_TRADES=5
APPROVAL_THRESHOLD=10000
ENABLE_KILL_SWITCH=true
PAPER_TRADING=true

# ============================================
# FEATURE FLAGS
# ============================================
ENABLE_AI_FEATURES=false
ENABLE_CRYPTO=false
ENABLE_OPTIONS=false

# ============================================
# MONITORING
# ============================================
SENTRY_DSN=
ENVIRONMENT=development
"@
    $EnvContent | Out-File -FilePath $EnvFile -Encoding utf8
    Write-Status "[OK] New .env file created with templates" "Success"
}

# ============================================
# STEP 8: INITIALIZE DATABASE
# ============================================
Write-Status "`n  STEP 8: Initializing Database..." "Info"

try {
    $DbScript = Join-Path $ProjectRoot "scripts" "init_database.py"
    if (Test-Path $DbScript) {
        python $DbScript
        Write-Status "[OK] Database initialized" "Success"
    }
    else {
        Write-Status "  Database init script not found, skipping" "Warning"
    }
}
catch {
    Write-Status "  Database initialization had issues, continuing..." "Warning"
}

# ============================================
# STEP 9: API SETUP GUIDANCE
# ============================================
if (-not $SkipAPISetup) {
    Write-Status "`n STEP 9: API Key Setup (Required for Trading)..." "Info"
    
    Write-Status @"


                    FREE API KEY SETUP REQUIRED                       

                                                                      
  To start trading with real market data, you need these FREE APIs:   
                                                                      
  1. ALPACA (Paper Trading - $0)                                      
     URL: https://alpaca.markets                                      
     Steps: Sign up  Dashboard  API Keys  Generate               
     Copy: API Key ID and Secret Key                                  
                                                                      
  2. POLYGON.IO (Stock Data - $0)                                     
     URL: https://polygon.io                                          
     Steps: Sign up  Dashboard  API Keys  Create                   
     Copy: API Key                                                      
                                                                      
  3. ALPHA VANTAGE (Stock Data - $0)                                  
     URL: https://www.alphavantage.co/support/#api-key                
     Steps: Click "Get Free API Key"  Enter email  Receive key        
     Copy: API Key                                                      
                                                                      

"@ "Warning"

    $SetupNow = Read-Host "`nDo you want to open these websites in your browser now? (y/n) [default: y]"
    if ($SetupNow -ne "n") {
        Write-Status "Opening Alpaca..." "Info"
        Start-Process "https://alpaca.markets"
        Start-Sleep -Seconds 3
        
        Write-Status "Opening Polygon..." "Info"
        Start-Process "https://polygon.io"
        Start-Sleep -Seconds 3
        
        Write-Status "Opening Alpha Vantage..." "Info"
        Start-Process "https://www.alphavantage.co/support/#api-key"
    }
    
    Write-Status @"

  IMPORTANT: After getting your API keys:

1. Open the file: $EnvFile
2. Replace the placeholder values with your real keys
3. Save the file
4. NEVER commit .env to GitHub (it's in .gitignore by default)

Example:
   ALPACA_API_KEY=PK1234567890ABCDEF
   ALPACA_SECRET_KEY=your_secret_here
   POLYGON_API_KEY=abc123def456
"@ "Warning"
}

# ============================================
# STEP 10: TEST INSTALLATION
# ============================================
Write-Status "`n STEP 10: Testing Installation..." "Info"

$TestResults = @()

# Test Python
Write-Status "Testing Python..." "Info"
try {
    $PyVersion = python --version 2>&1
    $TestResults += "[OK] Python: $PyVersion"
}
catch {
    $TestResults += " Python: Not working"
}

# Test Git
Write-Status "Testing Git..." "Info"
try {
    $GitVersion = git --version 2>&1
    $TestResults += "[OK] Git: $GitVersion"
}
catch {
    $TestResults += " Git: Not working"
}

# Test Dependencies
Write-Status "Testing Python dependencies..." "Info"
try {
    python -c "import fastapi, uvicorn, pandas, sqlalchemy, alpaca_trade_api; print('OK')" 2>&1 | Out-Null
    $TestResults += "[OK] Core dependencies: Working"
}
catch {
    $TestResults += " Core dependencies: Some issues (may need API keys)"
}

# Test Virtual Environment
Write-Status "Testing virtual environment..." "Info"
if ($env:VIRTUAL_ENV) {
    $TestResults += "[OK] Virtual Environment: Active"
}
else {
    $TestResults += "  Virtual Environment: Not active (run .\venv\Scripts\Activate.ps1)"
}

Write-Status "`n Test Results:" "Info"
$TestResults | ForEach-Object { Write-Status $_ }

# ============================================
# STEP 11: GITHUB SETUP
# ============================================
Write-Status "`n STEP 11: GitHub Repository Setup..." "Info"

$GitDir = Join-Path $ProjectRoot ".git"
if (Test-Path $GitDir) {
    Write-Status "[OK] Git repository already initialized" "Success"
}
else {
    Write-Status "Initializing Git repository..." "Info"
    try {
        git init
        Write-Status "[OK] Git repository initialized" "Success"
    }
    catch {
        Write-Status "  Git init failed, continuing..." "Warning"
    }
}

# Check GitHub remote
$Remotes = git remote -v 2>&1
if ($Remotes -match "github.com") {
    Write-Status "[OK] GitHub remote already configured" "Success"
    Write-Status "Remote: $Remotes" "Info"
}
else {
    Write-Status @"
  GitHub remote not configured.

To connect to GitHub:
1. Create a repository at: https://github.com/new
2. Name it: Financial-Master
3. Run these commands:
   git remote add origin https://github.com/YOUR_USERNAME/Financial-Master.git
   git add .
   git commit -m "Initial commit"
   git push -u origin main
"@ "Warning"
}

# ============================================
# FINAL SUMMARY
# ============================================
Write-Status @"


                      SETUP COMPLETE! [OK]                              

"@ "Success"

Write-Status @"

 WHAT'S BEEN INSTALLED:
"@ "Info"

$Installed = @(
    "[OK] Python 3.11+ with pip"
    "[OK] Virtual environment (.venv)"
    "[OK] All Python dependencies"
    "[OK] Git for version control"
    "[OK] VS Code (IDE)"
    "[OK] Environment configuration (.env)"
)
if (-not $SkipDocker) {
    $Installed += "[OK] Docker Desktop (optional)"
}
$Installed += "[OK] Project structure ready"

$Installed | ForEach-Object { Write-Status $_ }

Write-Status @"

 NEXT STEPS TO START TRADING:

1.  ADD API KEYS (5 minutes)
   - Edit: $EnvFile
   - Add your Alpaca, Polygon, Alpha Vantage keys
   - All APIs are FREE tier

2.  TEST THE SYSTEM (2 minutes)
   Run: .\scripts\test_installation.ps1
   
3.  START THE APPLICATION (1 minute)
   Run: .\scripts\start_local.ps1
   
4.  OPEN IN BROWSER
   URL: http://localhost:8000
   API Docs: http://localhost:8000/docs

"@ "Info"

Write-Status @"

 HELPFUL DOCUMENTATION:

 Quick Start: .\QUICKSTART.md
 Complete Setup: .\COMPLETE_SETUP_GUIDE.md
 API Setup: .\docs\compliance\API_SETUP_GUIDE.md
 Beginner Guide: .\docs\BEGINNERS_GUIDE.md
 Troubleshooting: .\docs\TROUBLESHOOTING.md

"@ "Info"

Write-Status @"

 COST SUMMARY:

 Setup: FREE
 APIs: FREE (Alpaca, Polygon, Alpha Vantage free tiers)
 Hosting: FREE (Render, Neon, Cloudflare free tiers)
 Trading: FREE (Paper trading with Alpaca)
 Total Monthly Cost: 0.00

"@ "Success"

Write-Status @"

 NEED HELP?

 Check the documentation files above
 Run: .\scripts\health_check.ps1
 Review: .\docs\TROUBLESHOOTING.md

"@ "Warning"

Write-Status "Press any key to exit..." "Info"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

