@echo off
REM Analyze corrections database and generate report

cd /d "%~dp0..\.."
python tools\corrections\analyze_corrections.py %*
pause

