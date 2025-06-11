@echo off
title PoE Leveling Planner
echo ============================================
echo PoE Leveling Planner v1.0.0
echo ============================================
echo.

echo Starting the application...
echo.
echo If you see import errors, run Install-Dependencies.bat first
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
    echo Application exited with error!
    echo ============================================
    echo.
    echo Please run Install-Dependencies.bat first
    echo.
    pause
)
