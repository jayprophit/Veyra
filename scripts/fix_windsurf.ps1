# Fix Windsurf automation issues
$ProjectRoot = "c:\Users\jpowe\Desktop\Financial Master"
Set-Location $ProjectRoot

Write-Host "Fixing Windsurf configuration..."

# 1. Fix Python venv
$venvPath = "$ProjectRoot\.venv"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

# 2. Update Windsurf settings
$settings = @'
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.extraPaths": [
    "${workspaceFolder}/src/backend",
    "${workspaceFolder}/src/backend/app"
  ],
  "windsurf.cascade.permissions": {
    "allowFileCreation": true,
    "allowCommandExecution": true,
    "allowGitOperations": true
  }
}
'@

$settings | Out-File -FilePath "$ProjectRoot\.windsurf\settings.json" -Encoding UTF8

# 3. Fix Git config
git config --global core.autocrlf true
git config --global safe.directory "*"
git config --global --add safe.directory $ProjectRoot

Write-Host "Windsurf configuration fixed!" -ForegroundColor Green
