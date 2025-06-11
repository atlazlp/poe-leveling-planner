@echo off
title PoE Leveling Planner - Installation
echo ============================================
echo PoE Leveling Planner v1.0.1 Installation
echo ============================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    py --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Python is not installed!
        echo Please install Python from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo Python found! Installing dependencies...
echo.

REM First try to install with the main requirements file
echo Attempting to install with main requirements.txt...
%PYTHON_CMD% -m pip install --user -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo.
    echo WARNING: Main requirements.txt installation failed!
    echo This is likely due to missing Visual C++ Build Tools.
    echo.
    echo Trying safe requirements (without lxml)...
    
    if exist requirements-safe.txt (
        %PYTHON_CMD% -m pip install --user -r requirements-safe.txt
        
        if %ERRORLEVEL% neq 0 (
            echo.
            echo ERROR: Failed to install even safe dependencies!
            echo Please check your internet connection and try again.
            echo.
            echo You may need to install Microsoft Visual C++ Build Tools
            echo Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
            pause
            exit /b 1
        ) else (
            echo.
            echo SUCCESS: Safe dependencies installed!
            echo Note: This version uses a slower HTML parser but should work fine.
        )
    ) else (
        echo.
        echo ERROR: requirements-safe.txt not found!
        echo Please ensure all files are extracted properly.
        pause
        exit /b 1
    )
) else (
    echo.
    echo SUCCESS: All dependencies installed successfully!
)

echo.
echo ============================================
echo Installation completed successfully!
echo ============================================
echo.
echo You can now run the application using:
echo   - Double-click "Start-PoE-Leveling-Planner.bat"
echo   - Or run: %PYTHON_CMD% main.py
echo.
pause
