@echo off
echo Batch Transcript Normalizer
echo.

cd /d "%~dp0"

echo Choose an option:
echo 1. Process first 10 files (test run)
echo 2. Process all files in batches of 10
echo 3. Process with custom batch size
echo 4. Process and keep temp directories for inspection
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Processing first 10 files as test run...
    python batch_normalizer.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --batch-size 10 --keep-temp --results-file ..\batch_results\test_batch_results.json
) else if "%choice%"=="2" (
    echo.
    echo Processing all files in batches of 10...
    python batch_normalizer.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --batch-size 10 --results-file ..\batch_results\full_batch_results.json
) else if "%choice%"=="3" (
    echo.
    set /p batch_size="Enter batch size: "
    echo Processing all files in batches of %batch_size%...
    python batch_normalizer.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --batch-size %batch_size% --results-file ..\batch_results\custom_batch_results.json
) else if "%choice%"=="4" (
    echo.
    echo Processing all files and keeping temp directories...
    python batch_normalizer.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --batch-size 10 --keep-temp --results-file ..\batch_results\inspection_batch_results.json
) else (
    echo Invalid choice.
)

echo.
echo Operation complete!
pause
