#!/usr/bin/env python3
"""
Build script for PoE Leveling Planner
Creates Windows installer and Linux AppImage with updated data
"""

import os
import sys
import json
import shutil
import subprocess
import platform
import zipfile
from pathlib import Path
from data_manager import DataManager

# Build configuration
APP_NAME = "PoE Leveling Planner"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Desktop overlay application for Path of Exile leveling assistance"
APP_AUTHOR = "PoE Leveling Planner Team"
APP_URL = "https://github.com/atlazlp/poe-leveling-planner"

# Default configuration template
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

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True, shell=True if isinstance(cmd, str) else False)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            raise
        return e

def update_all_data():
    """Update all game data by crawling latest information"""
    print_step("Updating Game Data")
    
    try:
        data_manager = DataManager()
        
        # Update data for all supported languages
        languages = ["en_US", "pt_BR"]
        
        for lang in languages:
            print(f"\nUpdating data for {lang}...")
            success = data_manager.force_update_all(lang)
            if success:
                print(f"✓ Successfully updated data for {lang}")
            else:
                print(f"✗ Failed to update data for {lang}")
                return False
        
        print("\n✓ All game data updated successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error updating game data: {e}")
        return False

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

def install_build_dependencies():
    """Install required build dependencies"""
    print_step("Installing Build Dependencies")
    
    # Install PyInstaller
    run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    if platform.system() == "Windows":
        # Install NSIS for Windows installer
        print("Please ensure NSIS is installed for Windows installer creation")
        print("Download from: https://nsis.sourceforge.io/Download")
    else:
        # Install AppImage tools for Linux
        try:
            run_command(["which", "appimagetool"], check=False)
            print("✓ appimagetool found")
        except:
            print("Installing AppImage tools...")
            run_command(["wget", "-O", "appimagetool", "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"])
            run_command(["chmod", "+x", "appimagetool"])

def build_executable():
    """Build the executable using PyInstaller"""
    print_step("Building Executable")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "poe-leveling-planner",
        "--add-data", "data:data",
        "--add-data", "lang:lang",
        "--add-data", "config.json:.",
        "--add-data", "quest_data_en.json:.",
        "--hidden-import", "tkinter",
        "--hidden-import", "pynput",
        "--hidden-import", "requests",
        "--hidden-import", "beautifulsoup4",
        "--hidden-import", "lxml",
        "--hidden-import", "pyperclip",
        "main.py"
    ]
    
    run_command(cmd)
    print("✓ Executable built successfully")

def create_windows_builds():
    """Create both Windows builds - compiled executable and antivirus-safe source"""
    print_step("Creating Windows Builds")
    
    # Create compiled portable executable
    build_executable()
    
    # Create portable package
    create_portable_package()
    
    # Create antivirus-safe source package
    create_antivirus_safe_package()
    
    print("✓ All Windows builds created successfully")

def create_portable_package():
    """Create a portable Windows package with the executable"""
    print_step("Creating Portable Executable Package")
    
    package_name = f"PoE-Leveling-Planner-v{APP_VERSION}-Windows-Portable"
    package_dir = Path("dist") / package_name
    
    # Clean previous package
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Create package directory
    package_dir.mkdir(parents=True)
    
    # Copy executable
    exe_src = Path("dist") / "poe-leveling-planner.exe"
    if exe_src.exists():
        shutil.copy2(exe_src, package_dir / "PoE-Leveling-Planner.exe")
    else:
        print("Warning: Executable not found!")
        return False
    
    # Copy necessary files
    shutil.copy2("config.json", package_dir / "config.json")
    
    if os.path.exists("lang"):
        shutil.copytree("lang", package_dir / "lang")
    if os.path.exists("data"):
        shutil.copytree("data", package_dir / "data")
    if os.path.exists("quest_data_en.json"):
        shutil.copy2("quest_data_en.json", package_dir / "quest_data_en.json")
    
    # Create README
    readme_content = f"""# {APP_NAME} v{APP_VERSION} - Portable Windows Edition

## Quick Start

1. Double-click `PoE-Leveling-Planner.exe` to start
2. Click the ⚙️ button to configure settings
3. Set up your character and gem preferences

## Features

- Transparent desktop overlay for Path of Exile
- Always centered positioning
- Quest reward tracking and gem progression
- Customizable hotkeys and appearance
- Multi-monitor support

## Requirements

- Windows 10 or later
- No additional software needed (standalone executable)

## Default Hotkeys

- Ctrl+1: Previous quest/step
- Ctrl+2: Next quest/step
- Ctrl+3: Copy quest search term

For more information, visit: {APP_URL}
"""
    
    with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Create ZIP archive
    zip_path = Path("dist") / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✓ Portable package created: {zip_path}")
    return True

def create_antivirus_safe_package():
    """Create an antivirus-safe source package for Windows"""
    print_step("Creating Antivirus-Safe Source Package")
    
    package_name = f"PoE-Leveling-Planner-v{APP_VERSION}-Windows-Safe"
    package_dir = Path("dist") / package_name
    
    # Clean previous package
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Create package directory
    package_dir.mkdir(parents=True)
    
    # Copy Python source files
    python_files = [
        "main.py", "config_gui.py", "config_manager.py", "data_manager.py",
        "language_manager.py", "quest_reward_crawler.py", "vendor_reward_crawler.py"
    ]
    
    for file in python_files:
        if os.path.exists(file):
            shutil.copy2(file, package_dir / file)
    
    # Copy other necessary files
    if os.path.exists("requirements.txt"):
        shutil.copy2("requirements.txt", package_dir / "requirements.txt")
    shutil.copy2("config.json", package_dir / "config.json")
    
    if os.path.exists("lang"):
        shutil.copytree("lang", package_dir / "lang")
    if os.path.exists("data"):
        shutil.copytree("data", package_dir / "data")
    if os.path.exists("quest_data_en.json"):
        shutil.copy2("quest_data_en.json", package_dir / "quest_data_en.json")
    
    # Create installation script
    install_script = f"""@echo off
title {APP_NAME} - Installation
echo ============================================
echo {APP_NAME} v{APP_VERSION} - Setup
echo ============================================
echo.

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

echo Python found! Installing dependencies...
%PYTHON_CMD% -m pip install --user -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo Double-click "Start-PoE-Leveling-Planner.bat" to run the application.
pause
"""
    
    with open(package_dir / "Install-Dependencies.bat", "w", encoding="utf-8") as f:
        f.write(install_script)
    
    # Create launcher script
    launcher_script = f"""@echo off
title {APP_NAME} - Antivirus Safe Edition
echo ============================================
echo {APP_NAME} v{APP_VERSION}
echo ============================================
echo.
echo Starting application (antivirus-safe source version)...
echo.

py main.py 2>nul || python main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Error starting application!
    echo Please run Install-Dependencies.bat first.
    pause
)
"""
    
    with open(package_dir / "Start-PoE-Leveling-Planner.bat", "w", encoding="utf-8") as f:
        f.write(launcher_script)
    
    # Create README
    readme_content = f"""# {APP_NAME} v{APP_VERSION} - Antivirus-Safe Windows Edition

## About This Version

This is a **source-based package** designed to avoid antivirus false positives.
Instead of a compiled executable, it runs Python source code directly.

## Quick Start

1. Run `Install-Dependencies.bat` (first time only)
2. Run `Start-PoE-Leveling-Planner.bat` to start the application

## Features

- **Antivirus Safe**: No compiled executable to trigger false positives
- **Same Functionality**: Identical features to the compiled version
- **Always Centered**: Overlay appears centered on screen
- **Multi-Monitor Support**: Choose your preferred monitor
- **Quest Tracking**: PoE quest rewards and gem progression

## Requirements

- Python 3.8+ installed on your system
- Internet connection for dependency installation

## Why This Version?

Some antivirus software incorrectly flags PyInstaller executables as malicious.
This source-based version avoids that issue entirely.

For more information, visit: {APP_URL}
"""
    
    with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Create ZIP archive
    zip_path = Path("dist") / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✓ Antivirus-safe package created: {zip_path}")
    return True

def create_linux_appimage():
    """Create Linux AppImage"""
    print_step("Creating Linux AppImage")
    
    appdir = Path("PoE-Leveling-Planner.AppDir")
    
    # Clean previous AppDir
    if appdir.exists():
        shutil.rmtree(appdir)
    
    # Create AppDir structure
    appdir.mkdir()
    (appdir / "usr" / "bin").mkdir(parents=True)
    (appdir / "usr" / "share" / "applications").mkdir(parents=True)
    (appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps").mkdir(parents=True)
    
    # Copy executable
    shutil.copy2("dist/poe-leveling-planner", appdir / "usr" / "bin" / "poe-leveling-planner")
    
    # Copy data files
    shutil.copytree("data", appdir / "usr" / "bin" / "data")
    shutil.copytree("lang", appdir / "usr" / "bin" / "lang")
    shutil.copy2("config.json", appdir / "usr" / "bin" / "config.json")
    shutil.copy2("quest_data_en.json", appdir / "usr" / "bin" / "quest_data_en.json")
    
    # Create desktop file
    desktop_content = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Comment={APP_DESCRIPTION}
Exec=poe-leveling-planner
Icon=poe-leveling-planner
Categories=Game;Utility;
Terminal=false
"""
    
    with open(appdir / "usr" / "share" / "applications" / "poe-leveling-planner.desktop", "w") as f:
        f.write(desktop_content)
    
    # Copy desktop file to AppDir root
    shutil.copy2(appdir / "usr" / "share" / "applications" / "poe-leveling-planner.desktop", appdir / "poe-leveling-planner.desktop")
    
    # Create AppRun script
    apprun_content = """#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
cd "${HERE}/usr/bin"
exec "${HERE}/usr/bin/poe-leveling-planner" "$@"
"""
    
    with open(appdir / "AppRun", "w") as f:
        f.write(apprun_content)
    
    os.chmod(appdir / "AppRun", 0o755)
    
    # Create icon (placeholder - you should add a real icon)
    icon_content = """#!/bin/bash
# Placeholder icon - replace with actual icon file
echo "Icon placeholder"
"""
    
    with open(appdir / "poe-leveling-planner.png", "w") as f:
        f.write("# Placeholder icon")
    
    # Create AppImage
    try:
        if os.path.exists("./appimagetool"):
            run_command(["./appimagetool", str(appdir), f"dist/PoE-Leveling-Planner-v{APP_VERSION}-x86_64.AppImage"])
        else:
            run_command(["appimagetool", str(appdir), f"dist/PoE-Leveling-Planner-v{APP_VERSION}-x86_64.AppImage"])
        
        print("✓ Linux AppImage created successfully")
        
        # Clean up
        shutil.rmtree(appdir)
        
    except Exception as e:
        print(f"✗ Failed to create AppImage: {e}")
        print("Please ensure appimagetool is installed")

def main():
    """Main build function"""
    print_step(f"Building {APP_NAME} v{APP_VERSION}")
    
    # Step 1: Update all game data
    if not update_all_data():
        print("✗ Failed to update game data. Build aborted.")
        return False
    
    # Step 2: Create default configuration
    create_default_config()
    
    # Step 3: Install build dependencies
    install_build_dependencies()
    
    # Step 4: Build executable
    build_executable()
    
    # Step 5: Create platform-specific packages
    if platform.system() == "Windows":
        create_windows_builds()
    else:
        create_linux_appimage()
    
    print_step("Build Complete!")
    
    # Show build results
    dist_files = list(Path("dist").glob("*"))
    if dist_files:
        print("\nBuild artifacts created:")
        for file in dist_files:
            print(f"  - {file}")
    
    print(f"\n✓ {APP_NAME} v{APP_VERSION} build completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nBuild interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Build failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 