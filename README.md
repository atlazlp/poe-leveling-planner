# PoE Leveling Planner

A desktop overlay application for Path of Exile that displays helpful information while playing, with global hotkey support for seamless interaction without changing the active window.

## Features

- **Transparent Overlay**: Semi-transparent overlay that stays on top of all windows
- **Global Hotkeys**: Control the overlay without switching windows
  - `Ctrl+X`: Change display text
  - `Ctrl+Z`: Return to original text
- **Corner Positioning**: Displays in the corner of your main monitor
- **Cross-Platform**: Works on Windows and Linux

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- pynput (for global hotkey detection)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/poe-leveling-planner.git
cd poe-leveling-planner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

1. Run the application - a semi-transparent overlay will appear in the top-right corner
2. Use `Ctrl+X` to toggle between different text displays
3. Use `Ctrl+Z` to return to the original text
4. The overlay will remain visible and accessible while playing Path of Exile

## Development

This project is built with:
- Python tkinter for the GUI overlay
- pynput for global hotkey detection
- Threading for non-blocking hotkey listening

## Future Features

- Path of Exile process detection (show overlay only when PoE is running)
- Leveling guides and skill tree information
- Item and currency tracking
- Build recommendations
- Configurable hotkeys and positioning 