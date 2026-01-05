# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A JARVIS-style (Iron Man inspired) system monitoring application with Python/tkinter. Features a rotating 3D Iron Man model, real-time CPU/Memory/GPU/Network stats, and scrolling code displays. Cross-platform support for macOS, Windows, and Linux.

## Commands

```bash
# macOS/Linux
./run.sh

# Windows
run.bat

# Manual launch (all platforms)
python system_monitor.py

# Pre-render 3D model frames (run once after cloning)
python prerender_model.py

# Install dependencies
pip install -r requirements.txt
```

## Architecture

**Main files:**
- `system_monitor.py` - Main application (JarvisMonitor class)
- `prerender_model.py` - Pre-renders 3D model rotation frames
- `ironman/files/` - STL model files
- `ironman/cache/` - Pre-rendered PNG frames and code cache

**Key components:**
- `setup_ui()` - Creates 3-column layout (CPU/Mem gauges, 3D model, Network stats)
- `update_stats()` - 1-second update loop for all metrics
- `animate_model()` - Cycles through pre-rendered frames at 20fps
- `scroll_code()` - Animates scrolling code displays
- `draw_arc_gauge()` - JARVIS-style arc gauges for CPU/Memory
- `draw_network_graph()` - Real-time network graph with history

## Cross-Platform Support

**Tested on:** macOS, Windows, Linux (Ubuntu)

**Platform-specific handling:**
- Disk usage: Uses `C:\` on Windows, `/` on Unix
- GPU detection: Identifies Apple Silicon, Intel Mac, Windows, Linux
- Battery: Shows percentage with charging indicator (⚡) or "AC" on desktops
- File paths: Uses `os.path.join()` for cross-platform compatibility

## Visual Theme

- JARVIS cyan (#00d4ff) primary color
- Orange (#ff6600) accent for upload/warnings
- Dark background (#0a0a12)
- Pre-rendered 3D Iron Man model with wireframe edges
- Scrolling code displays with fade effects

## Important: tkinter Memory Leak Pattern

**Never create `tkfont.Font` objects inside update loops.** Always pre-create fonts in `__init__`:

```python
# Good - create once in __init__
self.small_font = tkfont.Font(family='Courier', size=8)

# Bad - memory leak!
canvas.create_text(..., font=tkfont.Font(family='Courier', size=8))
```

## Pre-rendered Model System

The 3D model uses pre-rendered frames for performance:
1. `prerender_model.py` generates 120 PNG frames (one full rotation)
2. Frames cached in `ironman/cache/frame_*.png`
3. Main app loads frames into memory and cycles through them
4. Run `python prerender_model.py` if model files change
