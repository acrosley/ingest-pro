@echo off
echo Creating Call Recordings Database...
echo.

cd /d "%~dp0"
python create_database.py

echo.
echo Database creation complete!
pause
