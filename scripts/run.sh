#!/bin/bash

# PoE Leveling Planner - Startup Script
# This script starts the overlay application with proper error handling

echo "Starting PoE Leveling Planner..."
echo "================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3: sudo apt install python3"
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "Error: tkinter is not installed"
    echo "Please install tkinter: sudo apt install python3-tk"
    exit 1
fi

# Check if pynput is installed
if ! python3 -c "import pynput" &> /dev/null; then
    echo "Error: pynput is not installed"
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies"
        exit 1
    fi
fi

# Check if the application is already running
if pgrep -f "python3 main.py" > /dev/null; then
    echo "Warning: PoE Leveling Planner is already running"
    echo "PID: $(pgrep -f 'python3 main.py')"
    echo "To stop it, run: pkill -f 'python3 main.py'"
    exit 1
fi

echo "Starting overlay application..."
echo "The overlay will appear in the top-right corner of your screen"
echo "Hotkeys: Ctrl+X (change text), Ctrl+Z (original text)"
echo "Press Ctrl+C to stop the application"
echo ""

# Start the application
python3 main.py 