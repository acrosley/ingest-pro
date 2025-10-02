@echo off
REM Re-transcribe demo file with corrected Google Cloud STT settings

echo ========================================
echo Re-transcribing Demo File
echo ========================================
echo.
echo This will re-transcribe "test copy.wav" with:
echo   - MULAW encoding (correct!)
echo   - 8000 Hz sample rate
echo   - phone_call model
echo   - Phrase hints enabled
echo   - Timestamps included
echo.

REM Delete old transcripts to force re-transcription
if exist "demo\Transcripts\test copy.txt" (
    echo Deleting old transcript...
    del "demo\Transcripts\test copy.txt"
)

if exist "demo\Transcripts\test copy.confidence.json" (
    echo Deleting old confidence data...
    del "demo\Transcripts\test copy.confidence.json"
)

echo.
echo Copying audio file to trigger transcription...
copy "demo\Audio\test copy.wav" "test copy.wav" >nul

echo.
echo ========================================
echo Now run: python processor.py
echo ========================================
echo.
echo The processor will detect the new file and transcribe it.
echo Check demo\Transcripts\ for the new output!
echo.
pause

