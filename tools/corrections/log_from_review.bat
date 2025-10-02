@echo off
REM Log corrections from a saved review file

cd /d "%~dp0..\.."

if "%~1"=="" (
    echo Usage: log_from_review.bat ^<path_to_review_file.json^>
    echo.
    echo Example: log_from_review.bat output\x105_2025-07-10.11-33.review.json
    pause
    exit /b 1
)

python tools\corrections\log_review_actions.py "%~1"
pause

