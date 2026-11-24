@echo off
setlocal enabledelayedexpansion
title GRAMTWIN AI - Startup Launcher
echo ============================================================
echo           GRAMTWIN AI - GEOSPATIAL INTELLIGENCE PLATFORM
echo ============================================================
echo.

cd /d "%~dp0"
set PYTHONPATH=%~dp0

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in PATH! Please install Python or add it to PATH.
    pause
    exit /b 1
)

:: Check Node / npm
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js / npm was not found in PATH! Please install Node.js.
    pause
    exit /b 1
)

echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "GRAMTWIN Backend" cmd /k "cd /d "%~dp0" && set PYTHONPATH=%~dp0 && title GRAMTWIN Backend && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Starting Vite React Frontend on http://localhost:5173 ...
start "GRAMTWIN Frontend" cmd /k "cd /d "%~dp0frontend" && title GRAMTWIN Frontend && npm run dev"

echo [3/3] Waiting for backend server to become ready...
powershell -Command "for ($i=0; $i -lt 15; $i++) { try { $res = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/' -UseBasicParsing -TimeoutSec 1; if ($res.StatusCode -eq 200) { Write-Host 'Backend is ready!'; break } } catch { Start-Sleep -Milliseconds 600 } }"

echo.
echo ============================================================
echo   GRAMTWIN AI is running successfully!
echo   - Web Dashboard:  http://localhost:5173
echo   - Backend API:    http://127.0.0.1:8000
echo   - API Swagger:    http://127.0.0.1:8000/docs
echo ============================================================
echo.
echo Opening browser to http://localhost:5173 ...
start http://localhost:5173

exit /b 0
