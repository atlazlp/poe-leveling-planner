@echo off
title PoE Leveling Planner - Portable Edition
echo ============================================
echo PoE Leveling Planner v1.0.0
echo Antivirus-Safe Portable Edition
echo ============================================
echo.

echo Starting the application...
echo.
echo This runs directly from source code - no antivirus issues!
echo Press Ctrl+C to stop the application
echo Close this window to exit
echo.

REM Try python first, then py
python main.py 2>nul
if %ERRORLEVEL% neq 0 (
    py main.py
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo ============================================
    echo Python Error!
    echo ============================================
    echo.
    echo Please ensure Python is installed and dependencies are set up.
    echo Run setup_windows.bat if you haven't already.
    echo.
    pause
) 