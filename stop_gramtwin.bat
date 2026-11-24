@echo off
title Stop GRAMTWIN AI Services
echo Stopping GRAMTWIN AI Backend and Frontend processes...

:: Terminate processes listening on port 8000 (Backend) and port 5173 (Frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Terminating Backend PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo Terminating Frontend PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo GRAMTWIN AI services stopped successfully.
pause
