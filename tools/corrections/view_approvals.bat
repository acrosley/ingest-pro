@echo off
REM View detailed list of approved words

cd /d "%~dp0..\.."
python tools\corrections\view_approvals.py
pause

