@echo off
REM PoE Leveling Planner - Windows Release Builder
REM Creates all Windows packages for GitHub release

title PoE Leveling Planner - Windows Release Builder
echo ================================================================
echo   PoE Leveling Planner - Windows Release Builder
echo ================================================================
echo.
echo This script creates all Windows release packages:
echo  - Portable executable package (ZIP)
echo  - Antivirus-safe source package (ZIP)
echo  - Standalone executable
echo.

REM Check if Python is available
echo Checking Python installation...
py --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    python --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Python is not installed!
        echo Please install Python from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python
    )
) else (
    set PYTHON_CMD=py
)
echo Python found!

REM Check if pip is available
echo Checking pip installation...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: pip is required but not working.
    pause
    exit /b 1
)
echo pip found!

REM Install/upgrade required packages
echo.
echo Installing/upgrading build dependencies...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt
%PYTHON_CMD% -m pip install pyinstaller

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Run the build
echo.
echo Starting Windows release build...
%PYTHON_CMD% build.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

REM Show results
echo.
echo ================================================================
echo   Build completed successfully!
echo ================================================================
echo.
echo Created files in 'dist/' directory:

if exist "dist" (
    dir /b "dist"
    echo.
    echo File sizes:
    for %%f in (dist\*) do (
        echo   %%~nxf - %%~zf bytes
    )
) else (
    echo No dist directory found!
)

echo.
echo Windows release packages are ready for GitHub release!
echo Run 'python release.py' to create the GitHub release.
echo.
pause 