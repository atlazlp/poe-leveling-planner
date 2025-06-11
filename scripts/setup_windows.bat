@echo off
echo ============================================
echo PoE Leveling Planner - Windows Setup
echo ============================================
echo.

echo Checking Python installation...
py --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo.
echo Python found! Installing dependencies...
echo.

echo Installing required packages...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Setup completed successfully!
echo ============================================
echo.
echo You can now run the application using:
echo   - Double-click "run_windows.bat"
echo   - Or run: python main.py
echo.
pause 