# Directory Structure

This document describes the reorganized directory structure of the PoE Leveling Planner project.

## Overview

The project has been reorganized into a logical folder structure to improve maintainability and reduce clutter in the root directory.

## Directory Structure

```
poe-leveling-planner/
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
├── requirements-safe.txt       # Safe dependencies (fallback)
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
│
├── src/                        # Source code
│   ├── main.py                 # Main application logic
│   ├── config_gui.py           # Configuration GUI
│   ├── config_manager.py       # Configuration management
│   ├── data_manager.py         # Data management and caching
│   ├── language_manager.py     # Internationalization
│   ├── quest_reward_crawler.py # Quest data crawler
│   ├── vendor_reward_crawler.py# Vendor data crawler
│   ├── html_parser_utils.py    # HTML parsing utilities
│   ├── configure.py            # Configuration utilities
│   └── demo_gem_cards.py       # Demo/testing utilities
│
├── scripts/                    # Build and run scripts
│   ├── build.py                # Main build script
│   ├── build_windows_safe.py   # Safe Windows build
│   ├── build_windows_simple.py # Simple Windows build
│   ├── build_windows_release.bat # Windows release build
│   ├── build.bat               # Windows build batch
│   ├── build.sh                # Linux/Mac build
│   ├── release.py              # Release management
│   ├── release.sh              # Release script
│   ├── run_windows.bat         # Windows run script
│   ├── run.sh                  # Linux/Mac run script
│   ├── setup_windows.bat       # Windows setup
│   └── PoE-Leveling-Planner-Portable.bat # Portable launcher
│
├── docs/                       # Documentation
│   ├── README_WINDOWS.md       # Windows-specific documentation
│   ├── BUILD.md                # Build instructions
│   ├── BUILD-INSTRUCTIONS.md   # Detailed build guide
│   ├── GEMS_FEATURE_SUMMARY.md # Gem features documentation
│   ├── RELEASE.md              # Release notes
│   ├── RELEASE_QUICK_REFERENCE.md # Quick release guide
│   ├── USER-GUIDE.md           # User guide
│   ├── VISUAL_CPP_FIX.md       # Visual C++ troubleshooting
│   └── DIRECTORY_STRUCTURE.md  # This file
│
├── config/                     # Configuration files
│   ├── config.json             # Main configuration
│   ├── config.json.backup      # Configuration backup
│   └── poe-leveling-planner.spec # PyInstaller specification
│
├── tests/                      # Test files
│   ├── test_overlay.py         # Overlay tests
│   └── test_position.py        # Position tests
│
├── tools/                      # Utility tools
│   ├── diagnose_installation.py # Installation diagnostics
│   └── appimagetool            # AppImage tool (Linux)
│
├── data/                       # Data files
│   ├── quest_data_en.json      # Quest data
│   ├── quest_rewards_*.json    # Quest reward data (by language)
│   ├── vendor_rewards_*.json   # Vendor reward data (by language)
│   └── data_metadata.json      # Data update metadata
│
├── lang/                       # Language files
│   ├── en_US.json              # English translations
│   └── pt_BR.json              # Portuguese translations
│
├── build/                      # Build outputs (generated)
├── dist/                       # Distribution files (generated)
├── dist_safe/                  # Safe distribution files (generated)
└── .github/                    # GitHub workflows and templates
```

## Key Changes

### 1. **Source Code Organization**
- All Python source files moved to `src/` directory
- Import paths updated to work with new structure
- Relative paths used for data, config, and language files

### 2. **Build Scripts**
- All build and run scripts moved to `scripts/` directory
- Scripts updated to reference new file locations
- PyInstaller spec file moved to `config/` directory

### 3. **Documentation**
- All documentation moved to `docs/` directory
- Organized by purpose (build, user guide, troubleshooting, etc.)

### 4. **Configuration**
- Configuration files moved to `config/` directory
- Config manager updated to find files in new location

### 5. **Testing**
- Test files moved to `tests/` directory
- Organized for future test expansion

### 6. **Tools**
- Utility tools moved to `tools/` directory
- Includes diagnostic and build tools

## Usage

### Running the Application

From the root directory:
```bash
python main.py
```

To open configuration:
```bash
python main.py --config
```

### Building

From the root directory:
```bash
# Windows
python scripts/build.py

# Linux/Mac
./scripts/build.sh
```

### Development

When developing, you can work directly with files in the `src/` directory. The main entry point (`main.py`) automatically adds the `src/` directory to the Python path.

## Benefits

1. **Cleaner Root Directory**: Only essential files in root
2. **Logical Organization**: Related files grouped together
3. **Better Maintainability**: Easier to find and modify files
4. **Scalability**: Structure supports future growth
5. **Professional Layout**: Follows common project conventions

## Migration Notes

- All file references have been updated to use relative paths
- Import statements work correctly with new structure
- Build scripts reference correct file locations
- Configuration and data files found automatically

The reorganization maintains full backward compatibility while providing a much cleaner and more maintainable codebase. 