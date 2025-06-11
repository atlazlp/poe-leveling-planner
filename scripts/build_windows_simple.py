#!/usr/bin/env python3
"""
Simple Windows Build Script for PoE Leveling Planner
Creates a standalone executable and portable zip package
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

def build_executable():
    """Build the executable using PyInstaller"""
    print_step("Building Windows Executable")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    # PyInstaller command for Windows
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "PoE-Leveling-Planner",
        "--add-data", "config.json;.",
        "--add-data", "lang;lang",
        "--hidden-import", "tkinter",
        "--hidden-import", "pynput",
        "--hidden-import", "requests",
        "--hidden-import", "beautifulsoup4",
        "--hidden-import", "lxml",
        "--hidden-import", "pyperclip",
        "--hidden-import", "psutil",
        "main.py"
    ]
    
    # Add data directory if it exists
    if os.path.exists("data"):
        cmd.extend(["--add-data", "data;data"])
    
    # Add quest data if it exists
    if os.path.exists("quest_data_en.json"):
        cmd.extend(["--add-data", "quest_data_en.json;."])
    
    run_command(cmd)
    print("✓ Executable built successfully")

def create_portable_package():
    """Create a portable Windows package"""
    print_step("Creating Portable Package")
    
    package_name = f"PoE-Leveling-Planner-v{APP_VERSION}-Windows-Portable"
    package_dir = Path("dist") / package_name
    
    # Clean previous package
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Create package directory
    package_dir.mkdir(parents=True)
    
    # Copy executable
    exe_src = Path("dist") / "PoE-Leveling-Planner.exe"
    if exe_src.exists():
        shutil.copy2(exe_src, package_dir / "PoE-Leveling-Planner.exe")
    else:
        print("Warning: Executable not found!")
        return False
    
    # Copy configuration files
    shutil.copy2("config.json", package_dir / "config.json")
    
    # Copy language files
    if os.path.exists("lang"):
        shutil.copytree("lang", package_dir / "lang")
    
    # Copy data files if they exist
    if os.path.exists("data"):
        shutil.copytree("data", package_dir / "data")
    
    # Copy quest data if it exists
    if os.path.exists("quest_data_en.json"):
        shutil.copy2("quest_data_en.json", package_dir / "quest_data_en.json")
    
    # Create README for the package
    readme_content = f"""# {APP_NAME} v{APP_VERSION} - Portable Windows Edition

## Quick Start

1. Double-click `PoE-Leveling-Planner.exe` to start the application
2. A transparent overlay will appear on your screen
3. Click the ⚙️ (gear) button to configure settings
4. Set up your character and gem preferences

## Features

- Transparent desktop overlay for Path of Exile
- Quest reward tracking and gem progression
- Vendor reward information
- Customizable hotkeys and appearance
- Multi-monitor support
- Always centered positioning

## Default Hotkeys

- Ctrl+1: Previous quest/step
- Ctrl+2: Next quest/step
- Ctrl+3: Copy quest search term

## Configuration

- Click the ⚙️ button on the overlay to open settings
- Adjust opacity, size, monitor, and offsets
- Create character profiles and select gems
- Customize hotkeys

## Files

- `PoE-Leveling-Planner.exe` - Main application
- `config.json` - Configuration settings
- `lang/` - Language files
- `data/` - Game data (if included)

## Requirements

- Windows 10 or later
- No additional software needed (standalone executable)

## Support

For issues or updates, visit: https://github.com/atlazlp/poe-leveling-planner
"""
    
    with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Create launcher batch file
    launcher_content = f"""@echo off
title {APP_NAME}
echo Starting {APP_NAME}...
echo.
echo If you see any errors, try running as administrator.
echo Press Ctrl+C to stop the application.
echo.

PoE-Leveling-Planner.exe

if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    echo.
    pause
)
"""
    
    with open(package_dir / "Start-PoE-Leveling-Planner.bat", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print(f"✓ Portable package created: {package_dir}")
    
    # Create ZIP archive
    zip_path = Path("dist") / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✓ ZIP archive created: {zip_path}")
    
    return True

def main():
    """Main build function"""
    print_step(f"Building {APP_NAME} v{APP_VERSION} for Windows")
    
    try:
        # Step 1: Create default configuration
        create_default_config()
        
        # Step 2: Build executable
        build_executable()
        
        # Step 3: Create portable package
        create_portable_package()
        
        print_step("Build Complete!")
        
        # Show build results
        dist_files = list(Path("dist").glob("*"))
        if dist_files:
            print("\nBuild artifacts created:")
            for file in sorted(dist_files):
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  - {file.name} ({size_mb:.1f} MB)")
                else:
                    print(f"  - {file.name}/ (directory)")
        
        print(f"\n✓ {APP_NAME} v{APP_VERSION} Windows build completed successfully!")
        print("\nTo test:")
        print("1. Navigate to the dist/ folder")
        print("2. Extract the ZIP file or go into the portable directory")
        print("3. Run PoE-Leveling-Planner.exe")
        
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