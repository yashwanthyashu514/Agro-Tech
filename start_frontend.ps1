# AgroTech Frontend Startup Script (React + Vite)
$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Starting AgroTech Frontend Dashboard (React + Vite)      " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

Set-Location -Path "$PSScriptRoot\frontend"

Write-Host "-> Serving on http://localhost:5173" -ForegroundColor Cyan
Write-Host "-> Proxying /api to http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""

npm run dev
