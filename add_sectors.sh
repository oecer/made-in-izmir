#!/bin/bash
# Script to add sectors to the Made in Izmir database on cPanel
# This script activates the virtual environment and runs the Python script

echo "=========================================="
echo "Made in Izmir - Add Sectors Script"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please create a virtual environment first with: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo "Error: Django is not installed in the virtual environment!"
    echo "Please install requirements first with: pip install -r requirements.txt"
    exit 1
fi

# Run the sector addition script
echo "Running sector addition script..."
echo ""
python add_sectors.py

# Deactivate virtual environment
deactivate

echo ""
echo "=========================================="
echo "Script execution completed!"
echo "=========================================="
