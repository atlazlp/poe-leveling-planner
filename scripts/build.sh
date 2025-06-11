#!/bin/bash

# PoE Leveling Planner Build Script
# Builds Linux AppImage with updated data and clean configuration

set -e  # Exit on any error

echo "=========================================="
echo "  PoE Leveling Planner Build Script"
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

# Install/upgrade required packages
echo "Installing/upgrading required packages..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Make build script executable
chmod +x scripts/build.py

# Run the build
echo "Starting build process..."
python3 scripts/build.py

echo ""
echo "Build completed! Check the 'dist' directory for your AppImage."
echo ""
echo "To run the AppImage:"
echo "  chmod +x dist/PoE-Leveling-Planner-v1.0.1-x86_64.AppImage"
echo "  ./dist/PoE-Leveling-Planner-v1.0.1-x86_64.AppImage" 