# GRAMTWIN AI - PowerShell One-Click Runner
Write-Host "============================================================" -ForegroundColor Green
Write-Host "       GRAMTWIN AI - GEOSPATIAL INTELLIGENCE PLATFORM       " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

$RootPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend in separate process
Write-Host "[1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootPath'; `$env:PYTHONPATH='$RootPath'; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

# 2. Start Frontend in separate process
Write-Host "[2/3] Starting Vite React Frontend on http://localhost:5173 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootPath\frontend'; npm run dev"

# 3. Wait for backend readiness
Write-Host "[3/3] Waiting for backend server readiness..." -ForegroundColor Yellow
for ($i = 0; $i -lt 15; $i++) {
    try {
        $res = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -UseBasicParsing -TimeoutSec 1
        if ($res.StatusCode -eq 200) {
            Write-Host "Backend is online and operational!" -ForegroundColor Green
            break
        }
    } catch {
        Start-Sleep -Milliseconds 600
    }
}

Write-Host ""
Write-Host "GRAMTWIN AI is running successfully!" -ForegroundColor Green
Write-Host "  Web Dashboard:  http://localhost:5173" -ForegroundColor White
Write-Host "  Backend API:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  API Swagger:    http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Yellow

Start-Process "http://localhost:5173"
