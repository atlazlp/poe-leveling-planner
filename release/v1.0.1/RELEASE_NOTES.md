# PoE Leveling Planner v1.0.1 Release Notes

**Release Date**: 2025-06-11

## 🎉 What's New in v1.0.1

### 🗂️ **Major Code Reorganization**
- **Cleaner Project Structure**: Reorganized the entire codebase into logical directories
  - `src/` - All source code
  - `scripts/` - Build and run scripts
  - `docs/` - Documentation
  - `config/` - Configuration files
  - `tests/` - Test files
  - `tools/` - Utility tools
- **Better Maintainability**: Much easier to navigate and modify the codebase
- **Professional Layout**: Follows industry best practices

### 🔧 **Bug Fixes**
- Fixed DataManager metadata initialization issue
- Fixed config GUI error handling with lambda functions
- Improved error handling throughout the application
- Updated all file paths to work with new directory structure

### 🛡️ **Enhanced Windows Support**
- **Visual C++ Fix**: Improved handling of lxml dependency issues
- **Safe Installation**: Automatic fallback to html.parser when lxml fails
- **Better Error Messages**: More helpful diagnostic information
- **Installation Diagnostics**: New diagnostic tool to help troubleshoot issues

### 🌐 **Improved HTML Parsing**
- **Graceful Fallback**: Automatically falls back from lxml to html.parser
- **Better Compatibility**: Works on systems without Visual C++ build tools
- **Performance**: Still uses lxml when available for best performance

## 📦 **Available Downloads**

### Windows Users (Recommended)
- **`PoE-Leveling-Planner-v1.0.1-Windows-Executable.zip`**
  - ✅ Standalone executable (no Python required)
  - ✅ Just download, extract, and run
  - ✅ Best for most users

### Windows Users (Alternative)
- **`PoE-Leveling-Planner-v1.0.1-Windows-Safe.zip`**
  - ✅ Source code version (requires Python)
  - ✅ Antivirus-friendly (no compiled executable)
  - ✅ Includes automatic dependency installation
  - ✅ Good for users who prefer source code

## 🚀 **Installation Instructions**

### Windows Executable Version
1. Download `PoE-Leveling-Planner-v1.0.1-Windows-Executable.zip`
2. Extract the ZIP file
3. Run `PoE-Leveling-Planner.exe`
4. Right-click the overlay to configure

### Windows Safe Version
1. Download `PoE-Leveling-Planner-v1.0.1-Windows-Safe.zip`
2. Extract the ZIP file
3. Run `Install-Dependencies.bat` (first time only)
4. Run `Start-PoE-Leveling-Planner.bat`

## 🔧 **System Requirements**

- **Windows 10 or later**
- **For executable version**: No additional requirements
- **For safe version**: Python 3.8+ (automatically installed if needed)

## 🐛 **Known Issues**

- None currently known

## 🙏 **Acknowledgments**

Thanks to all users who reported issues and provided feedback!

## 📞 **Support**

- **GitHub Issues**: https://github.com/atlazlp/poe-leveling-planner/issues
- **Documentation**: Check the included README files

---

**Full Changelog**: https://github.com/atlazlp/poe-leveling-planner/compare/v1.0.0...v1.0.1
