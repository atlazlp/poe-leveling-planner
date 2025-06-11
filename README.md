# PoE Leveling Planner - Desktop Overlay

A transparent desktop overlay application for Path of Exile with global hotkey support, visual configuration interface, and comprehensive quest/vendor reward tracking.

[![GitHub release](https://img.shields.io/github/v/release/atlazlp/poe-leveling-planner)](https://github.com/atlazlp/poe-leveling-planner/releases)
[![GitHub downloads](https://img.shields.io/github/downloads/atlazlp/poe-leveling-planner/total)](https://github.com/atlazlp/poe-leveling-planner/releases)
[![License](https://img.shields.io/badge/license-Open%20Source-blue)](https://github.com/atlazlp/poe-leveling-planner)

## 🚀 Quick Start

### Download Pre-built Releases
**Recommended for most users**

Visit the [Releases page](https://github.com/atlazlp/poe-leveling-planner/releases) to download:

#### Linux
- **AppImage** (Portable): Download and run directly
  ```bash
  chmod +x PoE-Leveling-Planner-*.AppImage
  ./PoE-Leveling-Planner-*.AppImage
  ```

#### Windows *(Coming Soon)*
- **Installer**: Automatic installation with updates
- **Portable**: Standalone executable

#### From Source
- **Source Archive**: Complete source code with dependencies

### Build from Source
```bash
# Clone the repository
git clone https://github.com/atlazlp/poe-leveling-planner.git
cd poe-leveling-planner

# Install dependencies
pip3 install -r requirements.txt

# Run the application
python3 main.py
```

## ✨ Features

### 🎯 Core Overlay Features
- **Semi-transparent overlay** with configurable opacity (10%-100%)
- **Always on top** positioning for visibility during gameplay
- **Multi-monitor support** with automatic detection
- **Configurable positioning** (top-left, top-right, bottom-left, bottom-right, center)
- **X/Y offset controls** for precise positioning (-1500 to +1500 pixels)
- **Built-in control buttons**:
  - Close button (✕) to exit the application
  - Config button (⚙) to open configuration window
- **Global hotkeys** for quest navigation (customizable)
- **Multi-language support** (English, Portuguese)

### 🎮 Path of Exile Integration
- **Quest reward tracking** with comprehensive database
- **Vendor reward information** for efficient leveling
- **Gem progression planning** with skill tree integration
- **Real-time quest data** updated from official sources
- **Leveling route optimization** for different character builds

### ⚙️ Configuration Interface
- **Visual configuration GUI** with live preview
- **Real-time position testing** - see changes instantly
- **Monitor selection** with automatic detection
- **Appearance controls**: opacity, size, colors, fonts
- **Hotkey customization** with dropdown selections
- **Content management** for quest and reward data
- **Three-button interface**:
  - **Save & Restart**: Saves settings and automatically restarts overlay
  - **Cancel**: Exit without saving changes
  - **Reset to Default**: Restore all settings to defaults

### 🌐 Data Management
- **Automatic data updates** from Path of Exile sources
- **Offline mode support** with cached data
- **Custom quest tracking** and personal notes
- **Export/import functionality** for sharing configurations

## 📦 Installation

### System Requirements
- **Linux**: X11 or Wayland desktop environment
- **Windows**: Windows 10 or later *(future releases)*
- **Python**: 3.8+ (for source builds)
- **Memory**: 50MB RAM minimum
- **Storage**: 100MB free space

### Prerequisites (Source Build)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-dev python3-tk

# Install Python dependencies
pip3 install -r requirements.txt
```

## 🎮 Usage

### Running the Application
```bash
# From AppImage (Linux)
./PoE-Leveling-Planner-*.AppImage

# From source
python3 main.py
```

The overlay will appear with:
- Quest progression tracker
- Vendor reward information
- Navigation hotkeys
- Configuration access

### Global Hotkeys (Customizable)
- **Ctrl+1**: Previous quest/step
- **Ctrl+2**: Next quest/step  
- **Ctrl+3**: Copy current quest regex/search term

### Configuration
Access configuration via:
- Click the config button (⚙) on the overlay
- Run: `python3 config_gui.py`
- Use the system tray menu *(if available)*

## 🔧 Configuration

Settings are stored in `config.json`:

```json
{
    "display": {
        "monitor": "auto",
        "position": "top-right",
        "x_offset": 0,
        "y_offset": 0,
        "opacity": 0.8,
        "always_on_top": true
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
        "auto_hide_when_poe_not_running": false,
        "fade_in_duration": 0,
        "fade_out_duration": 0
    },
    "language": {
        "current": "en_US"
    }
}
```

## 🏗️ Development

### Project Structure
```
poe-leveling-planner/
├── main.py                    # Main overlay application
├── config_gui.py              # Visual configuration interface
├── config_manager.py          # Configuration management
├── data_manager.py            # Game data management
├── quest_reward_crawler.py    # Quest data crawler
├── vendor_reward_crawler.py   # Vendor data crawler
├── language_manager.py        # Multi-language support
├── build.py                   # Build script for releases
├── release.py                 # Release automation script
├── data/                      # Game data files
├── lang/                      # Language files
├── dist/                      # Build artifacts
└── requirements.txt           # Python dependencies
```

### Building

#### Linux AppImage
```bash
# Build AppImage
python3 build.py

# Output: dist/PoE-Leveling-Planner-v1.0.0-x86_64.AppImage
```

#### Windows *(Future)*
```batch
REM Build Windows installer
python build.py

REM Output: dist/PoE-Leveling-Planner-Setup-v1.0.0.exe
```

### Creating Releases

The project includes automated release management:

```bash
# Create a GitHub release with all artifacts
./release.sh

# Create a prerelease
./release.sh --prerelease
```

See [RELEASE.md](RELEASE.md) for detailed release documentation.

### Data Updates

Update game data from official sources:

```bash
# Update all quest and vendor data
python3 data_manager.py --update-all

# Update specific language
python3 data_manager.py --update --lang en_US
```

### Testing
```bash
# Run feature tests
python3 test_features.py

# Test overlay positioning
python3 test_position.py

# Test data management
python3 test_overlay.py
```

## 🌍 Multi-Language Support

Currently supported languages:
- **English** (en_US) - Complete
- **Portuguese** (pt_BR) - Complete

The application automatically detects multiple monitors and allows you to:
- Select which monitor to display the overlay on
- Position the overlay relative to the selected monitor
- Apply pixel-perfect positioning with X/Y offsets

## 🐛 Troubleshooting

### Common Issues

**Overlay not visible:**
- Check if it's positioned outside your screen area
- Use the configuration GUI to reposition
- Try resetting to defaults

**Hotkeys not working:**
- Ensure no other applications are using the same key combinations
- Try different hotkey combinations in the configuration
- Check terminal output for hotkey registration errors

**Data not updating:**
- Check internet connection for automatic updates
- Manually trigger update: `python3 data_manager.py --update-all`
- Verify data files in `data/` directory

**Configuration window issues:**
- Make sure you have tkinter installed (`python3-tk` package)
- Check that the config.json file is not corrupted
- Try deleting config.json to reset to defaults

**AppImage not running:**
- Ensure file is executable: `chmod +x PoE-Leveling-Planner-*.AppImage`
- Check for missing dependencies: `ldd PoE-Leveling-Planner-*.AppImage`
- Try running from terminal to see error messages

### Reset to Defaults
If you encounter issues, you can reset all settings:
1. Open the configuration GUI
2. Click "Reset to Default"
3. Or manually delete `config.json` and restart the application

### Getting Help
- Check the [Issues page](https://github.com/atlazlp/poe-leveling-planner/issues) for known problems
- Create a new issue with detailed error information
- Include your system information and configuration file

## 📋 Roadmap

### Upcoming Features
- [ ] **Windows builds** with installer and portable versions
- [ ] **macOS support** with app bundle and DMG
- [ ] **Automatic updates** with built-in updater
- [ ] **Build planner integration** with Path of Building
- [ ] **Live game state detection** for automatic progression
- [ ] **Community quest routes** sharing and importing
- [ ] **Performance optimizations** for lower resource usage
- [ ] **Plugin system** for custom extensions

### Long-term Goals
- [ ] **Mobile companion app** for offline planning
- [ ] **Web interface** for remote configuration
- [ ] **Statistics tracking** and leveling analytics
- [ ] **Integration with streaming tools** for content creators

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Ways to Contribute
- **Bug Reports**: Submit detailed issue reports
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Submit pull requests
- **Documentation**: Improve guides and documentation
- **Translations**: Add support for new languages
- **Testing**: Help test new features and releases

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with detailed description

### Code Style
- Follow PEP 8 for Python code
- Add docstrings for new functions and classes
- Include tests for new features
- Update documentation as needed

## 📄 License

This project is open source and available under the MIT License. Feel free to modify and distribute.

## 🙏 Acknowledgments

- **Path of Exile** community for inspiration and feedback
- **Contributors** who help improve the project
- **Grinding Gear Games** for creating Path of Exile
- **Open source libraries** that make this project possible

## 📞 Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/atlazlp/poe-leveling-planner/issues)
- **Discussions**: [Community discussions and questions](https://github.com/atlazlp/poe-leveling-planner/discussions)
- **Releases**: [Download latest versions](https://github.com/atlazlp/poe-leveling-planner/releases)

---

**Made with ❤️ for the Path of Exile community** 