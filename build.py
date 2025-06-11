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
        "position": "top-right",
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

def create_windows_installer():
    """Create Windows installer using NSIS"""
    print_step("Creating Windows Installer")
    
    nsis_script = f"""
!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{APP_VERSION}"
!define APP_PUBLISHER "{APP_AUTHOR}"
!define APP_URL "{APP_URL}"
!define APP_DESCRIPTION "{APP_DESCRIPTION}"

!include "MUI2.nsh"

Name "${{APP_NAME}}"
OutFile "dist/PoE-Leveling-Planner-Setup-v${{APP_VERSION}}.exe"
InstallDir "$PROGRAMFILES64\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\\poe-leveling-planner.exe"
    File /r "data"
    File /r "lang"
    File "config.json"
    File "quest_data_en.json"
    
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\poe-leveling-planner.exe"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\poe-leveling-planner.exe"
    
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "URLInfoAbout" "${{APP_URL}}"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\poe-leveling-planner.exe"
    Delete "$INSTDIR\\config.json"
    Delete "$INSTDIR\\quest_data_en.json"
    RMDir /r "$INSTDIR\\data"
    RMDir /r "$INSTDIR\\lang"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    DeleteRegKey HKCU "Software\\${{APP_NAME}}"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
SectionEnd
"""
    
    # Write NSIS script
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_script)
    
    # Create installer
    try:
        run_command(["makensis", "installer.nsi"])
        print("✓ Windows installer created successfully")
        
        # Clean up
        os.remove("installer.nsi")
        
    except Exception as e:
        print(f"✗ Failed to create Windows installer: {e}")
        print("Please ensure NSIS is installed and in PATH")

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
        create_windows_installer()
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