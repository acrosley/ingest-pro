@echo off
echo ========================================
echo  IngestPro - Call Transcription Processor
echo ========================================
echo.

REM Change to the project directory
echo [1/3] Switching to project directory...
cd /d "%~dp0"
echo    Current directory: %CD%
echo.

REM Activate virtual environment
echo [2/3] Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo    Virtual environment activated successfully
) else (
    echo    ERROR: Virtual environment not found at venv\Scripts\activate.bat
    echo    Please ensure you have created a virtual environment in the project directory
    pause
    exit /b 1
)
echo.

REM Check if processor.py exists
echo [3/3] Checking processor availability...
if not exist "processor.py" (
    echo    ERROR: processor.py not found in project directory
    echo    Please ensure you are running this from the correct location
    pause
    exit /b 1
)
echo    Processor found: processor.py
echo.

REM Display usage information
echo ========================================
echo  Usage Examples:
echo ========================================
echo.
echo  Single file:
echo    python processor.py "path\to\audio.wav"
echo.
echo  Batch processing:
echo    python processor.py "audio\*.wav"
echo.
echo  With demo file:
echo    python processor.py "demo\Audio\test.wav"
echo.

REM Check if arguments were provided
if "%~1"=="" (
    echo ========================================
    echo  No audio file specified
    echo ========================================
    echo.
    echo  Please provide an audio file path as an argument:
    echo    run_processor.bat "path\to\audio.wav"
    echo.
    echo  Or run the processor interactively:
    set /p audio_file="Enter audio file path: "
    if not "!audio_file!"=="" (
        echo.
        echo Starting transcription...
        echo ========================================
        python processor.py "!audio_file!"
    ) else (
        echo No file specified. Exiting...
    )
) else (
    echo ========================================
    echo  Starting transcription...
    echo ========================================
    echo.
    python processor.py %*
)

echo.
echo ========================================
echo  Processing complete!
echo ========================================
echo.
echo  Check the 'output' directory for results:
echo  - .txt files: Full transcripts
echo  - .confidence.json: Word-level confidence data
echo  - .review.json: Flagged words for manual review
echo.

REM Keep window open to see results
pause

