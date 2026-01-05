#!/bin/bash
# Build standalone executable for System Monitor on Linux/Ubuntu

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== JarvisMonitor Linux Build Script ==="

# Check for Python3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Install with:"
    echo "  sudo apt install python3 python3-venv python3-tk"
    exit 1
fi

# Check for tkinter
python3 -c "import tkinter" 2>/dev/null || {
    echo "Error: tkinter not found. Install with:"
    echo "  sudo apt install python3-tk"
    exit 1
}

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Check if pre-rendered frames exist
if [ ! -f "ironman/cache/frame_000.png" ]; then
    echo "Pre-rendered frames not found. Generating..."
    python prerender_model.py
fi

# Build with PyInstaller
echo "Building standalone executable..."
pyinstaller \
    --name=JarvisMonitor \
    --onedir \
    --windowed \
    --noconfirm \
    --add-data "ironman/cache:ironman/cache" \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=psutil \
    system_monitor.py

echo ""
echo "=================================================="
echo "Build complete!"
echo "Executable: $SCRIPT_DIR/dist/JarvisMonitor/JarvisMonitor"
echo ""
echo "To run:"
echo "  ./dist/JarvisMonitor/JarvisMonitor"
echo ""
echo "To distribute, copy the entire dist/JarvisMonitor/ folder"
echo "=================================================="
