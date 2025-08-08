@echo off
REM Top 10 Pony Voting Processing - One-Click Installer and Launcher
REM This batch file will run the Python installer script

echo.
echo =====================================
echo Top 10 Pony Voting Processing Setup
echo =====================================
echo.
echo This will automatically install and set up everything needed:
echo - Git (if not installed)
echo - Python 3.13.5 (if not installed)
echo - Poetry (if not installed)
echo - Clone/update the repository
echo - Set up the virtual environment
echo - Launch the application
echo.

pause

REM Try to run with python3 first, then python
python3 build_exe.py 2>nul
if %errorlevel% neq 0 (
    python build_exe.py 2>nul
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.13.5 from https://python.org
        echo Make sure to check "Add Python to PATH" during installation
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Setup completed!
pause
