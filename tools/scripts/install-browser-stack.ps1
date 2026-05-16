$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

python -m pip install -r (Join-Path $root "services\browser-automation\requirements-browser.txt")
python -m playwright install chromium

Write-Host "Optional browser automation stack installed." -ForegroundColor Green
