#!/usr/bin/env python3
"""
Build standalone executable for System Monitor
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import shutil

def main():
    # Ensure we're in the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    # Install PyInstaller if not present
    print("Checking PyInstaller...")
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

    # Check if pre-rendered frames exist
    cache_dir = os.path.join(project_dir, 'ironman', 'cache')
    frames_exist = os.path.exists(os.path.join(cache_dir, 'frame_000.png'))

    if not frames_exist:
        print("Pre-rendered frames not found. Generating...")
        subprocess.check_call([sys.executable, 'prerender_model.py'])

    # Determine platform-specific settings
    system = platform.system()

    if system == 'Windows':
        icon_option = []  # Add --icon=icon.ico if you have an icon
        name = 'JarvisMonitor.exe'
    elif system == 'Darwin':
        icon_option = []  # Add --icon=icon.icns if you have an icon
        name = 'JarvisMonitor'
    else:
        icon_option = []
        name = 'JarvisMonitor'

    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=JarvisMonitor',
        '--onedir',  # Create a directory (more reliable than onefile for tkinter)
        '--windowed',  # No console window
        '--noconfirm',  # Overwrite without asking
        # Add data files
        '--add-data', f'ironman/cache{os.pathsep}ironman/cache',
        # Hidden imports that PyInstaller might miss
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=psutil',
        # Main script
        'system_monitor.py',
    ]

    cmd.extend(icon_option)

    print(f"Building for {system}...")
    print(f"Command: {' '.join(cmd)}")

    subprocess.check_call(cmd)

    # Output location
    dist_dir = os.path.join(project_dir, 'dist', 'JarvisMonitor')

    print(f"\n{'='*50}")
    print(f"Build complete!")
    print(f"Executable location: {dist_dir}")
    print(f"{'='*50}")

    if system == 'Darwin':
        print("\nOn macOS, you can also create an .app bundle by running:")
        print("  pyinstaller --windowed --onedir --name=JarvisMonitor system_monitor.py")
    elif system == 'Windows':
        print(f"\nRun: {os.path.join(dist_dir, 'JarvisMonitor.exe')}")
    else:
        print(f"\nRun: {os.path.join(dist_dir, 'JarvisMonitor')}")


if __name__ == '__main__':
    main()
