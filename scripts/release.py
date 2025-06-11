#!/usr/bin/env python3
"""
Release script for PoE Leveling Planner
Creates GitHub releases with build artifacts using GitHub CLI
"""

import os
import sys
import json
import shutil
import subprocess
import platform
import zipfile
from pathlib import Path
from datetime import datetime

# Release configuration
APP_NAME = "PoE Leveling Planner"
APP_VERSION = "1.0.1"
REPO_NAME = "atlazlp/poe-leveling-planner"

def print_step(message):
    """Print a release step message"""
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

def get_version_from_build_script():
    """Extract version from build.py"""
    try:
        with open("build.py", "r") as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('APP_VERSION = '):
                    version = line.split('=')[1].strip().strip('"\'')
                    return version
        return APP_VERSION
    except Exception as e:
        print(f"Warning: Could not extract version from build.py: {e}")
        return APP_VERSION

def create_source_archive():
    """Create source code archive"""
    print_step("Creating Source Archive")
    
    version = get_version_from_build_script()
    archive_name = f"poe-leveling-planner-v{version}-source.zip"
    archive_path = Path("dist") / archive_name
    
    # Ensure dist directory exists
    Path("dist").mkdir(exist_ok=True)
    
    # Files and directories to include in source archive
    include_patterns = [
        "*.py",
        "*.md",
        "*.txt",
        "*.json",
        "*.sh",
        "*.bat",
        "data/",
        "lang/",
        ".gitignore"
    ]
    
    # Files and directories to exclude
    exclude_patterns = [
        "__pycache__/",
        "*.pyc",
        ".git/",
        "dist/",
        "build/",
        "*.AppImage",
        "appimagetool",
        "config.json.backup"
    ]
    
    print(f"Creating source archive: {archive_name}")
    
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(d.startswith(pattern.rstrip('/')) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(".")
                
                # Check if file should be excluded
                should_exclude = any(
                    str(relative_path).startswith(pattern.rstrip('/')) or
                    str(relative_path).endswith(pattern.lstrip('*'))
                    for pattern in exclude_patterns
                )
                
                if should_exclude:
                    continue
                
                # Check if file matches include patterns
                should_include = any(
                    str(relative_path).endswith(pattern.lstrip('*')) or
                    str(relative_path).startswith(pattern.rstrip('/')) or
                    pattern == str(relative_path)
                    for pattern in include_patterns
                )
                
                if should_include:
                    print(f"  Adding: {relative_path}")
                    zipf.write(file_path, f"poe-leveling-planner-v{version}/{relative_path}")
    
    print(f"✓ Source archive created: {archive_path}")
    return archive_path

def get_build_artifacts():
    """Get list of available build artifacts"""
    print_step("Identifying Build Artifacts")
    
    artifacts = {}
    dist_path = Path("dist")
    
    if not dist_path.exists():
        print("No dist directory found. Please run build script first.")
        return artifacts
    
    # Look for AppImage
    appimage_files = list(dist_path.glob("*.AppImage"))
    if appimage_files:
        artifacts["linux_appimage"] = appimage_files[0]
        print(f"✓ Found Linux AppImage: {appimage_files[0]}")
    
    # Look for Windows portable package
    portable_zips = list(dist_path.glob("*Windows-Portable*.zip"))
    if portable_zips:
        artifacts["windows_portable"] = portable_zips[0]
        print(f"✓ Found Windows portable package: {portable_zips[0]}")
    
    # Look for Windows antivirus-safe package
    safe_zips = list(dist_path.glob("*Windows-Safe*.zip"))
    if safe_zips:
        artifacts["windows_safe"] = safe_zips[0]
        print(f"✓ Found Windows antivirus-safe package: {safe_zips[0]}")
    
    # Look for standalone Windows executable
    exe_files = list(dist_path.glob("poe-leveling-planner.exe"))
    if exe_files:
        artifacts["windows_exe"] = exe_files[0]
        print(f"✓ Found Windows executable: {exe_files[0]}")
    
    # Look for macOS app bundle (for future builds)
    app_files = list(dist_path.glob("*.app"))
    if app_files:
        artifacts["macos_app"] = app_files[0]
        print(f"✓ Found macOS app: {app_files[0]}")
    
    # Look for macOS DMG (for future builds)
    dmg_files = list(dist_path.glob("*.dmg"))
    if dmg_files:
        artifacts["macos_dmg"] = dmg_files[0]
        print(f"✓ Found macOS DMG: {dmg_files[0]}")
    
    return artifacts

def generate_release_notes(version, artifacts):
    """Generate release notes based on available artifacts"""
    notes = f"""# {APP_NAME} v{version}

## What's New
- Desktop overlay application for Path of Exile leveling assistance
- Semi-transparent overlay with configurable opacity and positioning
- Multi-monitor support with automatic detection
- Global hotkey support for quest navigation
- Visual configuration interface with live preview
- Support for multiple languages (English, Portuguese)

## Downloads

### Linux
"""
    
    if "linux_appimage" in artifacts:
        notes += f"- **AppImage**: `{artifacts['linux_appimage'].name}` - Portable Linux application\n"
    
    notes += "\n### Windows\n"
    if "windows_portable" in artifacts:
        notes += f"- **Portable Package**: `{artifacts['windows_portable'].name}` - Standalone executable with all dependencies\n"
    if "windows_safe" in artifacts:
        notes += f"- **Antivirus-Safe**: `{artifacts['windows_safe'].name}` - Source package to avoid false positives\n"
    if "windows_exe" in artifacts:
        notes += f"- **Standalone Executable**: `{artifacts['windows_exe'].name}` - Single executable file\n"
    
    if not any(key.startswith("windows_") for key in artifacts):
        notes += "- Windows builds will be available in future releases\n"
    
    notes += "\n### macOS\n"
    if "macos_dmg" in artifacts:
        notes += f"- **DMG**: `{artifacts['macos_dmg'].name}` - macOS disk image\n"
    elif "macos_app" in artifacts:
        notes += f"- **App Bundle**: `{artifacts['macos_app'].name}` - macOS application bundle\n"
    else:
        notes += "- macOS builds will be available in future releases\n"
    
    notes += f"""
### Source Code
- **Source Archive**: Source code with all dependencies and build scripts

## Installation

### Linux (AppImage)
1. Download the AppImage file
2. Make it executable: `chmod +x PoE-Leveling-Planner-*.AppImage`
3. Run: `./PoE-Leveling-Planner-*.AppImage`

### Windows
- **Portable Package**: Extract ZIP and run `PoE-Leveling-Planner.exe`
- **Antivirus-Safe**: Extract ZIP, run `Install-Dependencies.bat`, then use `Start-PoE-Leveling-Planner.bat`
- **Standalone**: Download and run `poe-leveling-planner.exe` directly

### From Source
1. Download and extract the source archive
2. Install Python 3.8+ and dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## System Requirements
- **Linux**: X11 or Wayland desktop environment
- **Windows**: Windows 10 or later
- **macOS**: macOS 10.14 or later (future releases)
- **Python**: 3.8+ (for source builds and antivirus-safe version)

## Features
- Transparent desktop overlay with customizable opacity
- Multi-monitor support with automatic detection
- Global hotkeys for quest navigation (Ctrl+1, Ctrl+2, Ctrl+3)
- Visual configuration interface with live preview
- Support for multiple languages
- Always-on-top positioning for gameplay visibility

For detailed usage instructions, see the README.md file in the source archive.
"""
    
    return notes

def create_github_release(version, artifacts, source_archive, prerelease=False):
    """Create GitHub release using GitHub CLI"""
    print_step("Creating GitHub Release")
    
    tag_name = f"v{version}"
    release_title = f"{APP_NAME} v{version}"
    
    # Generate release notes
    release_notes = generate_release_notes(version, artifacts)
    
    # Write release notes to temporary file
    notes_file = Path("release_notes.md")
    with open(notes_file, "w", encoding="utf-8") as f:
        f.write(release_notes)
    
    try:
        # Create the release
        cmd = [
            r"C:\Program Files\GitHub CLI\gh.exe", "release", "create", tag_name,
            "--title", release_title,
            "--notes-file", str(notes_file),
            "--repo", REPO_NAME
        ]
        
        if prerelease:
            cmd.append("--prerelease")
        
        # Add all artifacts to the release
        upload_files = []
        
        # Add source archive
        if source_archive.exists():
            upload_files.append(str(source_archive))
        
        # Add build artifacts
        for artifact_type, artifact_path in artifacts.items():
            if artifact_path.exists():
                upload_files.append(str(artifact_path))
        
        # Add files to command
        cmd.extend(upload_files)
        
        print(f"Creating release {tag_name} with {len(upload_files)} files...")
        result = run_command(cmd)
        
        if result.returncode == 0:
            print(f"✓ Release {tag_name} created successfully!")
            print(f"✓ Uploaded {len(upload_files)} files")
            
            # Print release URL
            url_result = run_command([r"C:\Program Files\GitHub CLI\gh.exe", "release", "view", tag_name, "--repo", REPO_NAME, "--web"])
            
        else:
            print(f"✗ Failed to create release")
            return False
            
    except Exception as e:
        print(f"✗ Error creating release: {e}")
        return False
    finally:
        # Clean up temporary files
        if notes_file.exists():
            notes_file.unlink()
    
    return True

def main():
    """Main release function"""
    print_step(f"Starting Release Process for {APP_NAME}")
    
    # Get version
    version = get_version_from_build_script()
    print(f"Release version: {version}")
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("✗ Not in a git repository. Please run from the project root.")
        sys.exit(1)
    
    # Create source archive
    source_archive = create_source_archive()
    
    # Get build artifacts
    artifacts = get_build_artifacts()
    
    if not artifacts and not source_archive.exists():
        print("✗ No build artifacts or source archive found. Please build the project first.")
        sys.exit(1)
    
    # Ask for confirmation
    print(f"\nReady to create release v{version} with:")
    print(f"  - Source archive: {source_archive.name}")
    for artifact_type, artifact_path in artifacts.items():
        print(f"  - {artifact_type.replace('_', ' ').title()}: {artifact_path.name}")
    
    response = input("\nProceed with release? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Release cancelled.")
        sys.exit(0)
    
    # Ask if this should be a prerelease
    prerelease_response = input("Mark as prerelease? (y/N): ").strip().lower()
    prerelease = prerelease_response in ['y', 'yes']
    
    # Create the release
    success = create_github_release(version, artifacts, source_archive, prerelease)
    
    if success:
        print_step("Release Complete!")
        print("✓ GitHub release created successfully")
        print("✓ All artifacts uploaded")
        print(f"✓ Release URL: https://github.com/{REPO_NAME}/releases/tag/v{version}")
    else:
        print_step("Release Failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 