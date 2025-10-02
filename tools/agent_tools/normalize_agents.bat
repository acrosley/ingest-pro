@echo off
echo Agent Name Normalization Tool
echo =============================
echo.
echo This tool will normalize agent names in the database by:
echo - Consolidating duplicate entries (e.g., "Alex" and "Alex Alvarez")
echo - Using the full name format as the standard
echo - Creating a backup before making changes
echo.
echo Current agent names will be analyzed and you'll be prompted
echo to confirm any changes before they are applied.
echo.

cd /d "%~dp0"

REM Check if database exists in database_tools directory
if not exist "..\database_tools\call_recordings.db" (
    echo ERROR: Database file not found: ..\database_tools\call_recordings.db
    echo.
    echo Please ensure the database file exists in the database_tools directory.
    echo.
    pause
    exit /b 1
)

echo Database found: ..\database_tools\call_recordings.db
echo.
echo Starting agent name normalization...
echo.

python normalize_agent_names.py

echo.
echo Normalization process completed.
pause
