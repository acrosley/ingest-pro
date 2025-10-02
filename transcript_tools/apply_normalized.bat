@echo off
echo Apply Normalized Files
echo.

cd /d "%~dp0"

echo This will apply normalized files to your original directory.
echo.

echo Choose an option:
echo 1. Apply with backup (recommended)
echo 2. Apply without backup (use only if you already have a backup)
echo 3. Apply and cleanup temp directories
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Applying normalized files with backup...
    python apply_normalized_files.py "..\batch_results\full_batch_results.json" "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES"
) else if "%choice%"=="2" (
    echo.
    echo Applying normalized files without backup...
    python apply_normalized_files.py "..\batch_results\full_batch_results.json" "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --no-backup
) else if "%choice%"=="3" (
    echo.
    echo Applying normalized files with backup and cleanup...
    python apply_normalized_files.py "..\batch_results\full_batch_results.json" "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --cleanup
) else (
    echo Invalid choice.
)

echo.
echo Operation complete!
pause
