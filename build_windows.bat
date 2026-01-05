@echo off
REM Build standalone executable for System Monitor on Windows

cd /d "%~dp0"

echo === JarvisMonitor Windows Build Script ===

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Download from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if needed
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Check if pre-rendered frames exist
if not exist "ironman\cache\frame_000.png" (
    echo Pre-rendered frames not found. Generating...
    python prerender_model.py
)

REM Build with PyInstaller
echo Building standalone executable...
pyinstaller ^
    --name=JarvisMonitor ^
    --onedir ^
    --windowed ^
    --noconfirm ^
    --add-data "ironman\cache;ironman\cache" ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=psutil ^
    system_monitor.py

echo.
echo ==================================================
echo Build complete!
echo Executable: %~dp0dist\JarvisMonitor\JarvisMonitor.exe
echo.
echo To run: dist\JarvisMonitor\JarvisMonitor.exe
echo.
echo To distribute, copy the entire dist\JarvisMonitor\ folder
echo ==================================================
pause
