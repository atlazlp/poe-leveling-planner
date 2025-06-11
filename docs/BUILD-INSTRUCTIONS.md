# Build and Release Instructions

This document explains how to build and release PoE Leveling Planner for different platforms.

## Quick Build Commands

### Windows
```batch
# Build all Windows packages
build_windows_release.bat

# Or use Python directly
python build.py
```

### Linux
```bash
# Build Linux AppImage
python build.py
```

### Create GitHub Release
```bash
# Create release with GitHub CLI
python release.py
```

## Build Outputs

### Windows Builds
The Windows build process creates three packages:

1. **Portable Package** (`PoE-Leveling-Planner-v{version}-Windows-Portable.zip`)
   - Contains standalone executable with all dependencies
   - No installation required - just extract and run
   - ~20MB download

2. **Antivirus-Safe Package** (`PoE-Leveling-Planner-v{version}-Windows-Safe.zip`)
   - Python source code package to avoid antivirus false positives
   - Requires Python 3.8+ on target system
   - Includes automated setup scripts
   - ~1MB download

3. **Standalone Executable** (`poe-leveling-planner.exe`)
   - Single executable file
   - May trigger antivirus warnings
   - ~19MB file

### Linux Builds
- **AppImage** (`PoE-Leveling-Planner-v{version}-x86_64.AppImage`)
  - Portable Linux application
  - Works on most Linux distributions
  - No installation required

## Automated Release Process

### GitHub Actions
The repository includes automated GitHub Actions workflows that:
- Build packages for both Windows and Linux
- Create GitHub releases automatically
- Upload all build artifacts

### Manual Release Process
1. **Update version** in `build.py`
2. **Build packages**:
   - Windows: Run `build_windows_release.bat`
   - Linux: Run `python build.py`
3. **Create release**: Run `python release.py`
4. **Verify uploads** on GitHub releases page

## Build Requirements

### Windows
- Python 3.8+ (with pip)
- PyInstaller (`pip install pyinstaller`)
- All dependencies from `requirements.txt`

### Linux
- Python 3.8+ (with pip)
- PyInstaller (`pip install pyinstaller`)
- appimagetool (downloaded automatically)
- All dependencies from `requirements.txt`

## Troubleshooting

### Windows Antivirus Issues
If antivirus software flags the built executable:
1. The antivirus-safe package provides a workaround
2. Users can run from source using the portable launchers
3. Consider code signing for official releases

### Build Failures
1. **Missing dependencies**: Run `pip install -r requirements.txt pyinstaller`
2. **Permission errors**: Run as administrator if needed
3. **Path issues**: Ensure Python is in system PATH

### Release Upload Issues
1. **GitHub CLI not configured**: Run `gh auth login`
2. **Permission denied**: Check repository access tokens
3. **File size limits**: GitHub has 2GB limit per file

## Version Management

The version is managed in `build.py`:
```python
APP_VERSION = "1.0.0"
```

Update this before creating releases. The version is automatically used in:
- Package filenames
- GitHub release tags
- Application metadata

## Distribution Strategy

### For End Users
1. **Windows users**: Recommend portable package first, antivirus-safe if needed
2. **Linux users**: AppImage for maximum compatibility
3. **Power users**: Source builds for customization

### For Developers
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run directly: `python main.py`
4. Build packages as needed

## Security Considerations

### Code Signing
- Windows executables are not code signed (causes antivirus warnings)
- Consider purchasing code signing certificate for official releases
- Antivirus-safe package bypasses this issue

### Supply Chain
- All dependencies are from PyPI
- Build process is deterministic
- GitHub Actions provides build transparency 