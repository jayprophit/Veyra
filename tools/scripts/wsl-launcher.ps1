#!/usr/bin/env pwsh
# WSL Launcher for Veyra
# Run this to start Veyra in WSL2 Ubuntu

$projectPath = "C:\Users\jpowe\Desktop\Veyra"
$wslPath = "/mnt/c/Users/jpowe/Desktop/Veyra"

Write-Host "🚀 Starting Veyra in WSL2 Ubuntu..." -ForegroundColor Cyan

# Start WSL
wsl -d Ubuntu -e true

# Run automation script in WSL
wsl -d Ubuntu -e bash -c "cd '$wslPath' && ./scripts/automate_infrastructure.sh start"