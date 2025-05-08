#!/bin/bash

# Setup script for facatura on Unix/Linux/macOS
# This script creates a Python virtual environment and installs all dependencies

# Exit on error
set -e

echo "Setting up facatura development environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "Installing facatura in development mode..."
pip install -e .

echo ""
echo "Setup complete! The virtual environment has been created and dependencies installed."
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate the virtual environment when you're done, run:"
echo "  deactivate"
echo ""