#!/usr/bin/env python3
"""
Antivirus-Friendly Windows Build Script for PoE Leveling Planner
Creates a directory-based package that's less likely to trigger antivirus
"""

import os
import sys
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

# Build configuration
APP_NAME = "PoE Leveling Planner"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Desktop overlay application for Path of Exile leveling assistance"

# Default configuration template (updated without position)
DEFAULT_CONFIG = {
    "display": {
        "monitor": "auto",
        "custom_x": None,
        "custom_y": None,
        "opacity": 0.8,
        "always_on_top": True,
        "x_offset": 0,
        "y_offset": 0
    },
    "appearance": {
        "width": 250,
        "height": 250,
        "background_color": "#2b2b2b",
        "text_color": "#ffffff",
        "font_family": "Arial",
        "font_size": 10,
        "font_weight": "bold"
    },
    "hotkeys": {
        "previous_quest": "ctrl+1",
        "next_quest": "ctrl+2",
        "copy_regex": "ctrl+3"
    },
    "behavior": {
        "auto_hide_when_poe_not_running": False,
        "fade_in_duration": 0,
        "fade_out_duration": 0
    },
    "characters": {
        "profiles": [],
        "selected": None
    },
    "language": {
        "current": "en_US"
    }
}

def print_step(message):
    """Print a build step message"""
    print(f"\n{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}")

def create_default_config():
    """Create default configuration file"""
    print_step("Creating Default Configuration")
    
    config_path = Path("config.json")
    
    # Backup existing config if it exists
    if config_path.exists():
        backup_path = Path("config.json.backup")
        shutil.copy2(config_path, backup_path)
        print(f"Backed up existing config to {backup_path}")
    
    # Write default config
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    
    print("✓ Default configuration created")

def create_antivirus_safe_package():
    """Create an antivirus-safe package with Python source files"""
    print_step("Creating Antivirus-Safe Package")
    
    package_name = f"PoE-Leveling-Planner-v{APP_VERSION}-Windows-Safe"
    package_dir = Path("dist_safe") / package_name
    
    # Clean previous package
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Create package directory
    package_dir.mkdir(parents=True)
    
    # Copy Python source files
    python_files = [
        "main.py",
        "config_gui.py", 
        "config_manager.py",
        "data_manager.py",
        "language_manager.py",
        "quest_reward_crawler.py",
        "vendor_reward_crawler.py"
    ]
    
    print("Copying Python source files...")
    for file in python_files:
        if os.path.exists(file):
            shutil.copy2(file, package_dir / file)
            print(f"  ✓ {file}")
    
    # Copy requirements
    if os.path.exists("requirements.txt"):
        shutil.copy2("requirements.txt", package_dir / "requirements.txt")
        print("  ✓ requirements.txt")
    
    # Copy configuration files
    shutil.copy2("config.json", package_dir / "config.json")
    print("  ✓ config.json")
    
    # Copy language files
    if os.path.exists("lang"):
        shutil.copytree("lang", package_dir / "lang")
        print("  ✓ lang/ directory")
    
    # Copy data files if they exist
    if os.path.exists("data"):
        shutil.copytree("data", package_dir / "data")
        print("  ✓ data/ directory")
    
    # Copy quest data if it exists
    if os.path.exists("quest_data_en.json"):
        shutil.copy2("quest_data_en.json", package_dir / "quest_data_en.json")
        print("  ✓ quest_data_en.json")
    
    # Create installation script
    install_script = f"""@echo off
title {APP_NAME} - Installation
echo ============================================
echo {APP_NAME} v{APP_VERSION} Installation
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

%PYTHON_CMD% -m pip install --user -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
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
"""
    
    with open(package_dir / "Install-Dependencies.bat", "w", encoding="utf-8") as f:
        f.write(install_script)
    
    # Create launcher script
    launcher_script = f"""@echo off
title {APP_NAME}
echo ============================================
echo {APP_NAME} v{APP_VERSION}
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
"""
    
    with open(package_dir / "Start-PoE-Leveling-Planner.bat", "w", encoding="utf-8") as f:
        f.write(launcher_script)
    
    # Create quick start launcher (bypasses dependency check)
    quick_launcher = f"""@echo off
title {APP_NAME} - Quick Start
REM Quick launcher - assumes dependencies are already installed
python main.py 2>nul || py main.py
"""
    
    with open(package_dir / "Quick-Start.bat", "w", encoding="utf-8") as f:
        f.write(quick_launcher)
    
    # Create README file
    readme_content = f"""# {APP_NAME} v{APP_VERSION} - Antivirus-Safe Windows Edition

## Quick Start

### First Time Setup:
1. Run `Install-Dependencies.bat` to install Python packages
2. Run `Start-PoE-Leveling-Planner.bat` to start the application

### If Python is Already Set Up:
- Just run `Quick-Start.bat` for fastest startup

## What This Package Contains

This is a **source-based package** that doesn't trigger antivirus false positives.
Instead of a compiled executable, it runs the Python source code directly.

### Files:
- `*.py` - Python source files
- `requirements.txt` - Python package dependencies  
- `config.json` - Configuration settings
- `lang/` - Language files
- `data/` - Game data (if included)
- `Install-Dependencies.bat` - One-time setup script
- `Start-PoE-Leveling-Planner.bat` - Main launcher
- `Quick-Start.bat` - Fast launcher (no dependency check)

## Requirements

- **Python 3.8+** installed on your system
- Internet connection for first-time dependency installation

## Features

- **Antivirus Safe**: No compiled executable to trigger false positives
- **Transparent overlay** for Path of Exile
- **Quest reward tracking** and gem progression
- **Always centered positioning** (updated)
- **Customizable hotkeys** and appearance
- **Multi-monitor support**

## Default Hotkeys

- Ctrl+1: Previous quest/step
- Ctrl+2: Next quest/step
- Ctrl+3: Copy quest search term

## Troubleshooting

### Python Not Found
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart your computer after installation

### Import Errors
- Run `Install-Dependencies.bat` again
- Check internet connection
- Try running as administrator

### Overlay Not Visible
- Check if overlay is behind other windows
- Try different monitor positions in config
- Adjust opacity settings

## Support

For issues or updates: https://github.com/atlazlp/poe-leveling-planner

## Why This Version?

Some antivirus software incorrectly flags PyInstaller executables as malicious.
This source-based version avoids that issue entirely while providing the same functionality.
"""
    
    with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"✓ Antivirus-safe package created: {package_dir}")
    
    # Create ZIP archive
    zip_path = Path("dist_safe") / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✓ ZIP archive created: {zip_path}")
    
    return True

def main():
    """Main build function"""
    print_step(f"Building {APP_NAME} v{APP_VERSION} - Antivirus Safe Edition")
    
    try:
        # Step 1: Create default configuration
        create_default_config()
        
        # Step 2: Create antivirus-safe package
        create_antivirus_safe_package()
        
        print_step("Build Complete!")
        
        # Show build results
        dist_files = list(Path("dist_safe").glob("*"))
        if dist_files:
            print("\nBuild artifacts created in dist_safe/:")
            for file in sorted(dist_files):
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  - {file.name} ({size_mb:.1f} MB)")
                else:
                    print(f"  - {file.name}/ (directory)")
        
        print(f"\n✓ {APP_NAME} v{APP_VERSION} antivirus-safe build completed!")
        print("\n🛡️ This version is antivirus-friendly:")
        print("  - No compiled executable")
        print("  - Source code based")
        print("  - Requires Python (user probably already has it)")
        print("  - Same functionality as compiled version")
        print("\nTo test:")
        print("1. Navigate to the dist_safe/ folder")
        print("2. Extract the ZIP file")
        print("3. Run Install-Dependencies.bat (first time only)")
        print("4. Run Start-PoE-Leveling-Planner.bat")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Build failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nBuild interrupted by user")
        sys.exit(1) 