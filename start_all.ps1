# AgroTech Unified Startup Script
# Launches both backend and frontend servers

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " AgroTech AI Agriculture Intelligence System - Launcher  " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

$Root = $PSScriptRoot

Write-Host "Starting Backend in a new window..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$Root\start_backend.ps1"

Start-Sleep -Seconds 3

Write-Host "Starting Frontend in a new window..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$Root\start_frontend.ps1"

Write-Host ""
Write-Host "-> Backend:  http://127.0.0.1:8000 (Swagger: http://127.0.0.1:8000/docs)" -ForegroundColor Cyan
Write-Host "-> Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "All systems operational!" -ForegroundColor Green
