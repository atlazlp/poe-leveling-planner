# 🪟 PoE Leveling Planner - Windows Installation Guide

## 📋 Quick Start (Recommended)

### 1. Install Python
- Download Python from: https://www.python.org/downloads/
- **IMPORTANT**: ✅ Check "Add Python to PATH" during installation
- Install Python 3.8 or higher (3.11+ recommended)
- Restart your computer after installation

### 2. Setup Dependencies
- Double-click `setup_windows.bat`
- Wait for all dependencies to install
- The script will tell you when it's complete

### 3. Run the Application
- Double-click `run_windows.bat`
- The overlay will appear on your screen

## 🎮 Usage

### First Time Setup
1. When you first run the app, click the ⚙️ (gear) button on the overlay
2. Configure your character and gem selections
3. The overlay will show your selected quests and rewards

### Global Hotkeys (Default)
- **Ctrl+1**: Previous quest/step
- **Ctrl+2**: Next quest/step  
- **Ctrl+3**: Copy current quest search term

### Configuration
- Click the ⚙️ button on the overlay to access settings
- Adjust position, opacity, size, and hotkeys
- Select your character build and gem preferences

## 🔧 Manual Installation (Alternative)

If the batch files don't work, you can install manually:

```powershell
# 1. Check Python installation
python --version

# 2. Install dependencies
python -m pip install --upgrade pip
python -m pip install pynput==1.7.6 requests==2.31.0 beautifulsoup4==4.12.2 lxml==4.9.3 pyperclip==1.8.2 psutil

# 3. Run the application
python main.py
```

## 🏗️ Project Structure

- `main.py` - Main overlay application
- `config_gui.py` - Configuration interface  
- `setup_windows.bat` - Automated setup script
- `run_windows.bat` - Application launcher
- `requirements.txt` - Python dependencies
- `config.json` - Application settings

## 🐛 Troubleshooting

### Python Not Found
- Reinstall Python with "Add to PATH" checked
- Restart your computer
- Try using `py` instead of `python` in commands

### Import Errors
- Run `setup_windows.bat` again
- Check your internet connection
- Try manual pip install commands above

### Overlay Not Visible
- Check if the overlay is behind other windows
- Try different monitor positions in config
- Adjust opacity settings (may be too transparent)

### Global Hotkeys Not Working
- The app needs to be running with appropriate permissions
- Try running as administrator if needed
- Check hotkey conflicts with other software

## 🎯 Features

- **Transparent overlay** for Path of Exile
- **Quest reward tracking** with gem progression
- **Vendor reward information** 
- **Multi-monitor support**
- **Customizable hotkeys**
- **Real-time position adjustment**
- **Multi-language support**

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify Python installation with `python --version`
3. Ensure all dependencies are installed
4. Try running as administrator if permissions are an issue

## 🔄 Updates

To update the application:
1. Pull the latest changes from the repository
2. Run `setup_windows.bat` again to update dependencies
3. Your configuration will be preserved 