#!/usr/bin/env python3
"""
PoE Leveling Planner - Entry Point
Main entry point that imports and runs the application from the src directory.
"""

import sys
import os

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Import and run the main application
from main import main

if __name__ == "__main__":
    main() 