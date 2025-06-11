#!/bin/bash
# Release script wrapper for PoE Leveling Planner
# Usage: ./release.sh [--prerelease]

set -e

echo "PoE Leveling Planner - Release Script"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "build.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated with GitHub
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI"
    echo "Please run: gh auth login"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Warning: You have uncommitted changes"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Release cancelled"
        exit 1
    fi
fi

# Run the Python release script
echo "Starting release process..."
python3 release.py "$@"

echo "Release script completed!" 