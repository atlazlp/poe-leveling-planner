# Release Management Guide

This guide explains how to create releases for the PoE Leveling Planner using GitHub CLI and the automated release scripts.

## Prerequisites

1. **GitHub CLI**: Install and authenticate with GitHub CLI
   ```bash
   # Install GitHub CLI (if not already installed)
   sudo apt install gh  # Ubuntu/Debian
   # or download from https://cli.github.com/
   
   # Authenticate with GitHub
   gh auth login
   ```

2. **Build Artifacts**: Ensure you have built the application
   ```bash
   # Build Linux AppImage
   python3 build.py
   ```

3. **Git Repository**: Ensure you're in a git repository with committed changes
   ```bash
   git add .
   git commit -m "Prepare for release"
   git push origin main
   ```

## Creating a Release

### Quick Release (Recommended)
```bash
# Create a standard release
./release.sh

# Create a prerelease
./release.sh --prerelease
```

### Manual Release
```bash
# Run the Python script directly
python3 release.py
```

## Release Process

The release script performs the following steps:

1. **Version Detection**: Extracts version from `build.py`
2. **Source Archive Creation**: Creates a zip file with source code
3. **Artifact Detection**: Finds available build artifacts in `dist/`
4. **Release Notes Generation**: Creates comprehensive release notes
5. **GitHub Release Creation**: Uses GitHub CLI to create the release
6. **File Upload**: Uploads all artifacts to the release

## Supported Build Artifacts

The release system automatically detects and includes:

### Currently Supported
- **Linux AppImage** (`*.AppImage`): Portable Linux application
- **Source Archive** (`*-source.zip`): Complete source code with dependencies

### Future Support (Ready to Add)
- **Windows Installer** (`*Setup*.exe`): Windows installer with automatic updates
- **Windows Portable** (`*.exe`): Standalone Windows executable
- **macOS App Bundle** (`*.app`): macOS application bundle
- **macOS DMG** (`*.dmg`): macOS disk image

## Adding Windows Builds

To add Windows installer support to future releases:

### 1. Update Build Script
Ensure your `build.py` creates Windows installers in the `dist/` directory:

```python
# In build.py, add Windows build function
def create_windows_installer():
    """Create Windows installer using NSIS or similar"""
    # Your Windows build logic here
    # Should create files like:
    # - dist/PoE-Leveling-Planner-Setup-v1.0.0.exe (installer)
    # - dist/poe-leveling-planner.exe (portable)
```

### 2. Build on Windows
Run the build process on a Windows machine:

```batch
REM On Windows
python build.py
```

### 3. Release with Windows Artifacts
The release script will automatically detect and include Windows builds:

```bash
# The release script will now include:
# - Linux AppImage
# - Windows Installer
# - Windows Portable
# - Source Archive
./release.sh
```

## Release Configuration

### Version Management
The version is automatically extracted from `build.py`:

```python
# In build.py
APP_VERSION = "1.0.0"  # Update this for new releases
```

### Repository Configuration
Update the repository name in `release.py` if needed:

```python
# In release.py
REPO_NAME = "atlazlp/poe-leveling-planner"  # Update if repository changes
```

### Release Notes Customization
Modify the `generate_release_notes()` function in `release.py` to customize:
- Feature descriptions
- Installation instructions
- System requirements
- Download descriptions

## File Structure

```
poe-leveling-planner/
├── release.py          # Main release script
├── release.sh          # Shell wrapper script
├── build.py            # Build script (contains version)
├── dist/               # Build artifacts directory
│   ├── *.AppImage     # Linux AppImage
│   ├── *Setup*.exe    # Windows installer (future)
│   ├── *.exe          # Windows portable (future)
│   ├── *.app          # macOS app bundle (future)
│   ├── *.dmg          # macOS DMG (future)
│   └── *-source.zip   # Source archive (auto-generated)
└── RELEASE.md         # This documentation
```

## Release Workflow Examples

### Standard Release Workflow
```bash
# 1. Update version in build.py
vim build.py  # Change APP_VERSION = "1.1.0"

# 2. Build the application
python3 build.py

# 3. Commit changes
git add .
git commit -m "Release v1.1.0"
git push origin main

# 4. Create release
./release.sh

# 5. The script will:
#    - Create source archive
#    - Detect build artifacts
#    - Generate release notes
#    - Create GitHub release
#    - Upload all files
```

### Cross-Platform Release Workflow
```bash
# 1. Build on Linux
python3 build.py  # Creates AppImage

# 2. Build on Windows (future)
python build.py   # Creates Windows installer and portable

# 3. Build on macOS (future)
python3 build.py  # Creates macOS app bundle and DMG

# 4. Collect all artifacts in dist/
# 5. Create release from any platform
./release.sh
```

## Troubleshooting

### Common Issues

**"Not authenticated with GitHub CLI"**
```bash
gh auth login
gh auth status  # Verify authentication
```

**"No build artifacts found"**
```bash
# Ensure you've built the application
python3 build.py
ls dist/  # Check for build artifacts
```

**"Not in a git repository"**
```bash
# Ensure you're in the project root
pwd
ls -la .git  # Should exist
```

**"Version not found in build.py"**
```bash
# Check that build.py contains APP_VERSION
grep "APP_VERSION" build.py
```

### Manual Release Creation
If the automated script fails, you can create releases manually:

```bash
# Create release manually
gh release create v1.0.0 \
  --title "PoE Leveling Planner v1.0.0" \
  --notes "Release notes here" \
  dist/*.AppImage \
  dist/*-source.zip
```

## Security Considerations

- The release script only uploads files from the `dist/` directory
- Source archives exclude sensitive files (`.git/`, `__pycache__/`, etc.)
- GitHub CLI uses your authenticated credentials
- All uploads are to your own repository

## Future Enhancements

Planned improvements to the release system:

1. **Automated CI/CD**: GitHub Actions for automated builds and releases
2. **Code Signing**: Sign Windows and macOS builds for security
3. **Update Mechanism**: Built-in update checker for the application
4. **Multi-Architecture**: Support for ARM64 builds
5. **Package Managers**: Submit to package repositories (Snap, Flatpak, Chocolatey)

## Support

For issues with the release system:
1. Check this documentation
2. Verify GitHub CLI authentication
3. Ensure build artifacts exist
4. Check git repository status
5. Open an issue on the GitHub repository 