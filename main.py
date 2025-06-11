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

# Import and run the main application - specify the src.main module explicitly
import importlib.util
spec = importlib.util.spec_from_file_location("src_main", os.path.join(src_path, "main.py"))
src_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(src_main)

if __name__ == "__main__":
    src_main.main() 