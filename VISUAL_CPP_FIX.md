# Visual C++ Installation Error - Quick Fix

## The Problem
When running `Install-Dependencies.bat`, you may see an error like:
```
Microsoft Visual C++ 14.0 is required
error: Microsoft Visual C++ 14.0 or greater is required
```

This happens because the `lxml` package needs to compile C code during installation.

## Quick Solutions (Try in order)

### 1. 🚀 FASTEST: Use Safe Installation (Recommended)
The `Install-Dependencies.bat` script will automatically try this if the main installation fails:
- It will install all dependencies except `lxml`
- The app will work fine, just with slightly slower HTML parsing
- **No additional software needed!**

### 2. 🔧 Manual Safe Installation
If the automatic fallback doesn't work:
```bash
pip install -r requirements-safe.txt
```

### 3. 💻 Install Visual C++ Build Tools (If you want lxml)
Only do this if you specifically want the fastest HTML parsing:

1. Download **Visual C++ Build Tools** from:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. Install with these components:
   - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
   - ✅ Windows 10/11 SDK (latest version)

3. Restart your computer

4. Run `Install-Dependencies.bat` again

### 4. 🆘 Diagnostic Tool
Run this to identify exactly what's wrong:
```bash
python diagnose_installation.py
```

## Why This Happens
- `lxml` is written in C and needs compilation on Windows
- Most users don't have development tools installed
- The safe version uses Python's built-in HTML parser instead
- **Both versions work equally well** - lxml is just faster

## Which Version Should I Use?
- **For most users**: Use the safe installation (no Visual C++ needed)
- **For developers**: Install Visual C++ Build Tools if you want the fastest parsing

## Still Having Issues?
1. Run `python diagnose_installation.py`
2. Follow its recommendations
3. Make sure Python is properly installed
4. Try running as administrator

The application will work perfectly fine without lxml! 