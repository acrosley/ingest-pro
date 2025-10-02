@echo off
echo Call Recordings Database Query Tool
echo.

cd /d "%~dp0"
python query_database.py

echo.
echo Query tool closed.
pause
