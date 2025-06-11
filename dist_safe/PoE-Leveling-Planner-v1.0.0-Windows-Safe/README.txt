# PoE Leveling Planner v1.0.0 - Antivirus-Safe Windows Edition

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

### Installation Issues
- **FIRST**: Run `python diagnose_installation.py` to identify problems
- **Visual C++ Errors**: Use `Install-Dependencies.bat` (it will try safe fallbacks)
- **Still having issues**: Follow the diagnostic tool's recommendations

### Python Not Found
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart your computer after installation

### Import Errors
- Run `Install-Dependencies.bat` again
- Check internet connection
- Try running as administrator
- **If lxml fails**: This is normal on some systems - the app will work fine without it

### Overlay Not Visible
- Check if overlay is behind other windows
- Try different monitor positions in config
- Adjust opacity settings

## Support

For issues or updates: https://github.com/atlazlp/poe-leveling-planner

## Why This Version?

Some antivirus software incorrectly flags PyInstaller executables as malicious.
This source-based version avoids that issue entirely while providing the same functionality.
