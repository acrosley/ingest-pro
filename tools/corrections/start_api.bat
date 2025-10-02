@echo off
REM Start the Corrections Logging API Server

cd /d "%~dp0..\.."

echo.
echo Starting Corrections Logging API Server...
echo This will run in the background while you review transcripts.
echo.

python tools\corrections\corrections_api.py

pause

