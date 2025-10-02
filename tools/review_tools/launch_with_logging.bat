@echo off
REM Launch AssemblyAI Review UI with Automatic Corrections Logging

echo.
echo ========================================
echo AssemblyAI Review System with Auto-Logging
echo ========================================
echo.
echo Starting servers...
echo.

REM Start the corrections API server in a new window
start "Corrections API Server" cmd /k "cd /d "%~dp0..\.." && python tools\corrections\corrections_api.py"

REM Wait a moment for API to start
timeout /t 2 /nobreak >nul

REM Start the review UI server in a new window
start "Review UI Server" cmd /k "cd /d "%~dp0" && python launch_assemblyai_review.py"

echo.
echo [OK] Servers launched!
echo.
echo Two windows have opened:
echo   1. Corrections API Server (port 5555) - Logs actions to database
echo   2. Review UI Server (port 8000) - Review interface
echo.
echo Open your browser to: http://localhost:8000
echo.
echo Keep both windows open while reviewing.
echo Close this window when done.
echo.
pause

