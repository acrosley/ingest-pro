@echo off
echo ========================================
echo Archive and Normalize JSON Files
echo ========================================
echo.

cd /d "%~dp0\.."

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run start_venv.bat first to set up the environment
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Virtual environment activated.
echo.

REM Check if source directory exists
if not exist "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" (
    echo ERROR: Source directory not found
    echo Expected: W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES
    echo.
    pause
    exit /b 1
)

echo Source directory found.
echo.

REM Show what will be done
echo This tool will:
echo 1. Archive original JSON files to ALL_JSON_FILES_BACKUP
echo 2. Normalize transcript data in ALL_JSON_FILES (working directory)
echo 3. Fix parsing errors like 'str' object has no attribute 'get'
echo.

echo Options:
echo 1. Dry run (show what would be done)
echo 2. Process with backup protection
echo 3. Force overwrite existing backups
echo 4. Exit
echo.

set /p choice="Select option (1-4): "

if "%choice%"=="1" (
    echo Running dry run...
    python database_tools\archive_and_normalize.py --dry-run
    goto end
)
if "%choice%"=="2" (
    echo Processing with backup protection...
    python database_tools\archive_and_normalize.py
    goto end
)
if "%choice%"=="3" (
    echo Force processing ^(will overwrite existing backups^)...
    set /p confirm="Are you sure? This will overwrite existing backups (y/N): "
    if /i "%confirm%"=="y" (
        python database_tools\archive_and_normalize.py --force
    ) else (
        echo Operation cancelled.
    )
    goto end
)
if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
)
echo Invalid choice. Exiting...
exit /b 1

:end

echo.
echo Processing complete!
pause
