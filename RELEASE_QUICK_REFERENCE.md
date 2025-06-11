# Release Quick Reference

## TL;DR - Create a Release

```bash
# Standard release
./release.sh

# Prerelease
./release.sh --prerelease
```

## Prerequisites Checklist

- [ ] GitHub CLI installed and authenticated (`gh auth status`)
- [ ] Build artifacts exist (`ls dist/`)
- [ ] Git changes committed and pushed
- [ ] Version updated in `build.py` if needed

## What Gets Released

### Current (Linux)
- ✅ **AppImage**: `PoE-Leveling-Planner-v1.0.0-x86_64.AppImage`
- ✅ **Source**: `poe-leveling-planner-v1.0.0-source.zip` (auto-generated)

### Future (Windows) - Ready to Add
- 🔄 **Installer**: `PoE-Leveling-Planner-Setup-v1.0.0.exe`
- 🔄 **Portable**: `poe-leveling-planner.exe`

### Future (macOS) - Ready to Add
- 🔄 **DMG**: `PoE-Leveling-Planner-v1.0.0.dmg`
- 🔄 **App Bundle**: `PoE-Leveling-Planner.app`

## File Structure

```
dist/
├── *.AppImage          # Linux (current)
├── *Setup*.exe         # Windows installer (future)
├── *.exe               # Windows portable (future)
├── *.dmg               # macOS DMG (future)
├── *.app               # macOS app (future)
└── *-source.zip        # Source (auto-generated)
```

## Common Commands

```bash
# Check what will be released
ls dist/

# Check version
grep "APP_VERSION" build.py

# Build before release
python3 build.py

# Create release
./release.sh

# Manual release (if script fails)
gh release create v1.0.0 --title "PoE Leveling Planner v1.0.0" dist/*
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `gh: command not found` | Install GitHub CLI: `sudo apt install gh` |
| `Not authenticated` | Run: `gh auth login` |
| `No artifacts found` | Run: `python3 build.py` |
| `Not in git repo` | Check you're in project root |
| `Version not found` | Check `APP_VERSION` in `build.py` |

## Adding Windows Builds Later

1. **Build on Windows**: Run `python build.py` on Windows machine
2. **Copy artifacts**: Copy `*.exe` files to `dist/` directory
3. **Release**: Run `./release.sh` - Windows builds will be auto-detected

The release system is already configured to handle Windows builds automatically! 