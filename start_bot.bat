@echo off
title MT5 Trading Bot Starter
color 0A
echo ============================================================
echo               MT5 Automated Trading Bot Starter
echo ============================================================
echo.
echo Starting MT5 Trading Bot...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found in current directory.
    echo Please ensure you're running this from the correct folder.
    pause
    exit /b 1
)

REM Start the bot
echo Running: python main.py
echo.
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ERROR: Bot exited with error code %errorlevel%
    echo Check the logs above for details.
    pause
) else (
    echo.
    echo Bot exited normally.
    pause
)