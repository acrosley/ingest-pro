@echo off
setlocal

pushd "%~dp0"

REM Decide which Python launcher to use (prefer py -3, fallback to python)
set "PY_CMD=py -3"
%PY_CMD% -V >nul 2>&1
if errorlevel 1 set "PY_CMD=python"

REM Local venv for this tool
set "VENV_DIR=%~dp0venv"
if not exist "%VENV_DIR%\Scripts\activate.bat" (
  echo Creating local venv for smart_rename using %PY_CMD% ...
  %PY_CMD% -m venv "%VENV_DIR%"
)

if exist "%VENV_DIR%\Scripts\activate.bat" (
  call "%VENV_DIR%\Scripts\activate.bat"
  python -m pip install --upgrade pip >nul 2>&1
  if exist requirements.txt (
    pip install -r requirements.txt >nul 2>&1
  )
) else (
  echo WARNING: Could not create/activate venv. Running with system Python.
)

echo Running smart_rename.py %*
python smart_rename.py %*

popd
pause


