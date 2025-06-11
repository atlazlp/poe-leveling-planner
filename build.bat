@echo off
REM PoE Leveling Planner Build Script for Windows
REM Builds Windows installer with updated data and clean configuration

echo ==========================================
echo   PoE Leveling Planner Build Script
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not installed.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is required but not installed.
    pause
    exit /b 1
)

REM Install/upgrade required packages
echo Installing/upgrading required packages...
pip install --upgrade pip
pip install -r requirements.txt

REM Run the build
echo Starting build process...
python build.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed! Check the 'dist' directory for your installer.
echo.
echo The installer will be named: PoE-Leveling-Planner-Setup-v1.0.0.exe
echo.
echo Note: NSIS must be installed for Windows installer creation.
echo Download from: https://nsis.sourceforge.io/Download
echo.
pause 