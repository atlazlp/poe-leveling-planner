# Build Instructions for PoE Leveling Planner

This document explains how to build distributable packages for the PoE Leveling Planner application.

## Overview

The build system automatically:
1. **Updates all game data** by crawling the latest information from PoE databases
2. **Creates a clean default configuration** with offset 0 and cleared character info, gems, and vendor selections
3. **Builds platform-specific packages** (Windows installer or Linux AppImage)

## Quick Start

### Linux (AppImage)
```bash
./build.sh
```

### Windows (Installer)
```batch
build.bat
```

### Manual Build (Any Platform)
```bash
python3 build.py
```

## Prerequisites

### Common Requirements
- Python 3.7 or higher
- pip (Python package manager)
- Internet connection (for data crawling)

### Windows Additional Requirements
- **NSIS (Nullsoft Scriptable Install System)**
  - Download from: https://nsis.sourceforge.io/Download
  - Add to PATH or install in default location

### Linux Additional Requirements
- **AppImage tools** (automatically downloaded if not present)
- Standard build tools (`gcc`, `make` - usually pre-installed)

## Build Process Details

### Step 1: Data Update
- Crawls quest reward data from PoEDB
- Crawls vendor reward data from PoE Wiki
- Updates data for all supported languages (English, Portuguese)
- Validates data integrity

### Step 2: Configuration Reset
- Creates a clean default configuration
- Sets offset to 0 (x_offset: 0, y_offset: 0)
- Clears character profiles and selections
- Resets gem and vendor selections
- Maintains other settings like hotkeys and appearance

### Step 3: Package Creation

#### Windows Installer (.exe)
- Creates a professional NSIS-based installer
- Includes uninstaller
- Creates Start Menu and Desktop shortcuts
- Registers in Windows Add/Remove Programs
- Bundles all data files and dependencies

#### Linux AppImage (.AppImage)
- Creates a portable AppImage that runs on most Linux distributions
- No installation required - just download and run
- Includes all dependencies
- Works on systems with different library versions

## Build Outputs

### Windows
- `dist/PoE-Leveling-Planner-Setup-v1.0.0.exe` - Windows installer

### Linux
- `dist/PoE-Leveling-Planner-v1.0.0-x86_64.AppImage` - Linux AppImage

## Default Configuration

The build process creates a clean configuration with these settings:

```json
{
    "display": {
        "monitor": "auto",
        "position": "top-right",
        "x_offset": 0,
        "y_offset": 0,
        "opacity": 0.8
    },
    "characters": {
        "profiles": [],
        "selected": null
    }
}
```

## Troubleshooting

### Windows Build Issues

**NSIS not found:**
```
Error: makensis command not found
```
- Install NSIS from https://nsis.sourceforge.io/Download
- Ensure NSIS is in your PATH

**Python not found:**
```
Error: Python is required but not installed
```
- Install Python from https://python.org
- Ensure Python is in your PATH

### Linux Build Issues

**AppImage tools not found:**
- The build script automatically downloads appimagetool
- Ensure you have internet connection and write permissions

**Permission denied:**
```
Permission denied: ./build.sh
```
- Run: `chmod +x build.sh`

### Common Issues

**Data update failed:**
- Check internet connection
- Verify PoEDB and PoE Wiki are accessible
- Try running the build again (temporary network issues)

**PyInstaller errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Try updating PyInstaller: `pip install --upgrade pyinstaller`

## Advanced Usage

### Custom Build Configuration

Edit `build.py` to modify:
- App version and metadata
- Default configuration template
- Build flags and options
- Package naming

### Manual Data Update Only

```python
from data_manager import DataManager
dm = DataManager()
dm.force_update_all_data("en_US")
```

### Custom Configuration

To build with a specific configuration, modify the `DEFAULT_CONFIG` in `build.py` before building.

## Distribution

### Windows
- Distribute the `.exe` installer file
- Users run the installer to install the application
- Application appears in Start Menu and can be uninstalled normally

### Linux
- Distribute the `.AppImage` file
- Users make it executable: `chmod +x PoE-Leveling-Planner-*.AppImage`
- Users run directly: `./PoE-Leveling-Planner-*.AppImage`
- No installation required

## Development Notes

- The build process is designed to be reproducible
- All external data is fetched fresh during each build
- Configuration is reset to ensure clean distribution
- Build artifacts are placed in the `dist/` directory
- Temporary build files are automatically cleaned up 