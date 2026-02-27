@echo off
REM setlist-dl Windows launcher
REM Passes all arguments through to the Python script

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found. Install from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

python "%~dp0setlist-dl.py" %*
