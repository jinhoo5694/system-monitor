@echo off
REM Complete build + installer creation script for Windows
REM This creates JarvisMonitor_Setup.exe that you can send to friends

cd /d "%~dp0"

echo ========================================
echo JarvisMonitor Windows Installer Creator
echo ========================================
echo.

REM Step 1: Build the executable
echo [1/2] Building executable...
call build_windows.bat

if not exist "dist\JarvisMonitor\JarvisMonitor.exe" (
    echo ERROR: Build failed. JarvisMonitor.exe not found.
    pause
    exit /b 1
)

REM Step 2: Create installer with Inno Setup
echo.
echo [2/2] Creating installer...

REM Try common Inno Setup locations
set ISCC=""
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"

if %ISCC%=="" (
    echo.
    echo Inno Setup not found. To create an installer:
    echo   1. Download from: https://jrsoftware.org/isdl.php
    echo   2. Install Inno Setup 6
    echo   3. Run this script again
    echo.
    echo Alternatively, just zip the dist\JarvisMonitor folder and share it.
    echo Your friend can run JarvisMonitor.exe directly from the folder.
    pause
    exit /b 0
)

REM Create installer output directory
if not exist installer mkdir installer

%ISCC% installer_windows.iss

if exist "installer\JarvisMonitor_Setup.exe" (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Installer created: installer\JarvisMonitor_Setup.exe
    echo.
    echo Send this file to your friend. They just double-click
    echo to install JarvisMonitor with desktop shortcut.
    echo ========================================
) else (
    echo.
    echo Installer creation failed. You can still share
    echo the dist\JarvisMonitor folder as a portable version.
)

pause
