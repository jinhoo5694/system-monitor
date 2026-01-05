# System Monitor - Hacker Theme

A lightweight system monitoring application with a hacker-style (black & green) theme, optimized for 1024x768 displays.

## Features

- **CPU Monitoring**: Real-time CPU usage with animated line graph showing 60-second history
- **Memory Monitoring**: Memory usage graph with percentage and used/total display
- **GPU Monitoring**: GPU status detection (Apple Silicon & Intel Mac)
- **Network Monitoring**: Dual-line graph showing upload/download speeds over time with total data transferred
- **Visual Graphs**: Smooth animated line graphs with grid overlay and axis labels for easy reading
- **Hacker Theme**: Black background with Matrix-style green (#00FF41) text and graphs
- **Lightweight**: Minimal resource usage using tkinter Canvas and psutil (no heavy dependencies like matplotlib)

## Installation

### 1. Install tkinter (if not already installed)

For Homebrew Python on macOS:
```bash
brew install python-tk@3.13
```

Or use the system Python which typically includes tkinter.

### 2. Dependencies

The virtual environment is already set up with all dependencies installed.

If you need to reinstall dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Easy Launch (Recommended)
Simply run the launch script:
```bash
./run.sh
```

### Manual Launch
Activate the virtual environment and run:
```bash
source venv/bin/activate
python3 system_monitor.py
```

## Requirements

- Python 3.6+
- psutil library
- tkinter (included with Python on macOS)

## Display Settings

The application is optimized for 1024x768 resolution. It will automatically size to fit your mini display.
