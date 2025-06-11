@echo off
echo ============================================
echo PoE Leveling Planner - Desktop Overlay
echo ============================================
echo.
echo Starting the application...
echo.
echo Press Ctrl+C to stop the application
echo Close this window to exit
echo.

py main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ============================================
    echo Application exited with error!
    echo ============================================
    echo.
    echo If you see import errors, please run setup_windows.bat first
    echo.
    pause
) 