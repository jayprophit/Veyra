# PowerShell script to fix all lint warnings in Veyra
# Fixes: Markdown lint, Python format, general project cleanup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Veyra - Lint Fix Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Working in: $projectRoot" -ForegroundColor Gray
Write-Host ""

# 1. Fix Markdown lint issues
Write-Host "1. Fixing Markdown lint warnings..." -ForegroundColor Yellow

# Fix PYTHON_INTERPRETER_SETUP.md
$mdFile = Join-Path $projectRoot "PYTHON_INTERPRETER_SETUP.md"
if (Test-Path $mdFile) {
    $content = Get-Content $mdFile -Raw
    
    # Add blank lines around fenced code blocks
    $content = $content -replace '(?<!
)(
```)', "`n`$1"
    $content = $content -replace '(```
)(?!
)', "`$1`n"
    
    # Add blank lines around headings
    $content = $content -replace '(?<!
)(#{1,6} )', "`n`$1"
    $content = $content -replace '(#{1,6} .*?
)(?!
)', "`$1`n"
    
    # Fix trailing spaces
    $content = $content -replace ' +\n', "`n"
    
    Set-Content $mdFile $content -NoNewline
    Add-Content $mdFile ""  # Ensure trailing newline
    Write-Host "   Fixed: PYTHON_INTERPRETER_SETUP.md" -ForegroundColor Green
}

# Fix CI_FAILURES_RESOLUTION.md
$ciFile = Join-Path $projectRoot "CI_FAILURES_RESOLUTION.md"
if (Test-Path $ciFile) {
    $content = Get-Content $ciFile -Raw
    $content = $content -replace ' +\n', "`n"
    $content = $content -replace '(?<!
)(#{1,6} )', "`n`$1"
    $content = $content -replace '(#{1,6} .*?
)(?!
)', "`$1`n"
    
    Set-Content $ciFile $content -NoNewline
    Add-Content $ciFile ""
    Write-Host "   Fixed: CI_FAILURES_RESOLUTION.md" -ForegroundColor Green
}

# Fix README.md
$readmeFile = Join-Path $projectRoot "README.md"
if (Test-Path $readmeFile) {
    $content = Get-Content $readmeFile -Raw
    $content = $content -replace ' +\n', "`n"
    
    Set-Content $readmeFile $content -NoNewline
    Add-Content $readmeFile ""
    Write-Host "   Fixed: README.md" -ForegroundColor Green
}

# 2. Fix Python lint issues
Write-Host ""
Write-Host "2. Running Black formatter on Python files..." -ForegroundColor Yellow

$venvPath = Join-Path $projectRoot ".venv"
if (Test-Path $venvPath) {
    $blackPath = Join-Path $venvPath "Scripts\black.exe"
    if (Test-Path $blackPath) {
        & $blackPath src/backend/app --line-length 100 2>$null
        Write-Host "   Black formatting complete" -ForegroundColor Green
    } else {
        Write-Host "   Black not found, skipping Python formatting" -ForegroundColor Yellow
    }
}

# 3. Fix GitHub template
Write-Host ""
Write-Host "3. Fixing GitHub template whitespace..." -ForegroundColor Yellow

$prTemplate = Join-Path $projectRoot ".github\pull_request_template.md"
if (Test-Path $prTemplate) {
    $content = Get-Content $prTemplate -Raw
    # Remove trailing spaces
    $content = $content -replace ' +\n', "`n"
    # Add proper heading
    if (-not $content.StartsWith("# ")) {
        $content = "# Pull Request`n`n" + $content
    }
    
    Set-Content $prTemplate $content -NoNewline
    Add-Content $prTemplate ""
    Write-Host "   Fixed: pull_request_template.md" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Lint fixes completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Run tests: .venv\Scripts\pytest tests/" -ForegroundColor Yellow
Write-Host "2. Push changes: git add . && git commit -m 'Fix: Resolve lint warnings'" -ForegroundColor Yellow
Write-Host ""
