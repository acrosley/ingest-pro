@echo off
echo Database Updater
echo.

cd /d "%~dp0"

echo Choose an option:
echo 1. Update database with new JSON files
echo 2. Show database statistics
echo.

set /p choice="Enter your choice (1-2): "

if "%choice%"=="1" (
    echo.
    echo Updating database with new JSON files...
    python database_updater.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES"
) else if "%choice%"=="2" (
    echo.
    echo Showing database statistics...
    python database_updater.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --stats
) else (
    echo Invalid choice.
)

echo.
echo Operation complete!
pause
