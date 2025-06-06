# PoE Leveling Planner - Desktop Overlay

A transparent desktop overlay application for Path of Exile with global hotkey support and visual configuration interface.

## Features

### Overlay Features
- **Semi-transparent overlay** with configurable opacity (10%-100%)
- **Always on top** positioning for visibility during gameplay
- **Multi-monitor support** with automatic detection
- **Configurable positioning** (top-left, top-right, bottom-left, bottom-right, center)
- **X/Y offset controls** for precise positioning (-1500 to +1500 pixels)
- **Built-in control buttons**:
  - Close button (✕) to exit the application
  - Config button (⚙) to open configuration window
- **Global hotkeys** for text switching (customizable)
- **Customizable text content** with default and alternate states

### Configuration Interface
- **Visual configuration GUI** with live preview
- **Real-time position testing** - see changes instantly
- **Monitor selection** with automatic detection
- **Appearance controls**: opacity, size, colors, fonts
- **Hotkey customization** with dropdown selections
- **Text content editing** for both default and alternate states
- **Three-button interface**:
  - **Save & Restart**: Saves settings and automatically restarts overlay
  - **Cancel**: Exit without saving changes
  - **Reset to Default**: Restore all settings to defaults

## Installation

### Prerequisites
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-dev python3-tk

# Install Python dependencies
pip3 install -r requirements.txt
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/atlazlp/poe-leveling-planner.git
cd poe-leveling-planner

# Install dependencies
pip3 install -r requirements.txt

# Run the overlay
python3 main.py

# Or open configuration first
python3 config_gui.py
```

## Usage

### Running the Overlay
```bash
python3 main.py
```

The overlay will appear on your screen with:
- Default text content
- Close button (✕) in top-right corner
- Config button (⚙) next to close button
- Hotkey instructions at the bottom

### Configuration
Click the config button (⚙) on the overlay or run:
```bash
python3 config_gui.py
```

The configuration window provides:
- **Live preview** - red overlay shows exactly where your overlay will appear
- **Monitor selection** - choose between detected monitors
- **Position controls** - select corner or center positioning
- **X/Y offset sliders** - fine-tune position with pixel precision
- **Opacity slider** - adjust transparency (0.1 to 1.0)
- **Size controls** - set width and height
- **Hotkey selection** - customize toggle and reset keys
- **Text editing** - modify default and alternate text content

### Hotkeys (Customizable)
- **Ctrl+1** (default): Toggle to alternate text
- **Ctrl+2** (default): Return to original text

## Configuration File

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
        "height": 100,
        "background_color": "#2b2b2b",
        "text_color": "#ffffff",
        "font_family": "Arial",
        "font_size": 10,
        "font_weight": "bold"
    },
    "hotkeys": {
        "toggle_text": "ctrl+1",
        "reset_text": "ctrl+2"
    },
    "content": {
        "default_text": "PoE Leveling Planner\nReady to assist!",
        "alternate_text": "Hotkey Activated!\nCtrl+2 to return"
    }
}
```

## Multi-Monitor Support

The application automatically detects multiple monitors and allows you to:
- Select which monitor to display the overlay on
- Position the overlay relative to the selected monitor
- Apply pixel-perfect positioning with X/Y offsets

## Development

### Project Structure
```
poe-leveling-planner/
├── main.py              # Main overlay application
├── config_gui.py        # Visual configuration interface
├── config_manager.py    # Configuration management
├── config.json          # Settings file (auto-generated)
├── requirements.txt     # Python dependencies
├── test_features.py     # Feature test suite
└── README.md           # This file
```

### Testing
Run the test suite to verify all features:
```bash
python3 test_features.py
```

## Troubleshooting

### Common Issues

**Overlay not visible:**
- Check if it's positioned outside your screen area
- Use the configuration GUI to reposition
- Try resetting to defaults

**Hotkeys not working:**
- Ensure no other applications are using the same key combinations
- Try different hotkey combinations in the configuration
- Check terminal output for hotkey registration errors

**Configuration window issues:**
- Make sure you have tkinter installed (`python3-tk` package)
- Check that the config.json file is not corrupted

### Reset to Defaults
If you encounter issues, you can reset all settings:
1. Open the configuration GUI
2. Click "Reset to Default"
3. Or manually delete `config.json` and restart the application

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests. 