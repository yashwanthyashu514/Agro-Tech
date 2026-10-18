# AgroTech Backend Startup Script (FastAPI + Uvicorn)
$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Starting AgroTech AI Backend (FastAPI + Uvicorn)         " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

Set-Location -Path "$PSScriptRoot\backend"

Write-Host "-> Serving on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "-> Interactive Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "-> Health Endpoint: http://127.0.0.1:8000/health" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
