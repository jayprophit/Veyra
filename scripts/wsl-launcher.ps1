#!/usr/bin/env pwsh
# WSL Launcher for Financial Master
# Run this to start Financial Master in WSL2 Ubuntu

$projectPath = "C:\Users\jpowe\Desktop\Financial Master"
$wslPath = "/mnt/c/Users/jpowe/Desktop/Financial Master"

Write-Host "🚀 Starting Financial Master in WSL2 Ubuntu..." -ForegroundColor Cyan

# Start WSL
wsl -d Ubuntu -e true

# Run automation script in WSL
wsl -d Ubuntu -e bash -c "cd '$wslPath' && ./scripts/automate_infrastructure.sh start"