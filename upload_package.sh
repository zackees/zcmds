#!/usr/bin/env bash

# Exit on error and print commands as they're executed
set -e
set -x

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Ensure latest build tools
echo "Updating build tools..."
python -m pip install --upgrade pip build twine wheel

# Build the package
echo "Building Source and Wheel distribution..."
python -m build

# Upload to PyPI
echo "Uploading the package to PyPI..."
python -m twine upload dist/* --verbose

echo "Package upload complete!"
