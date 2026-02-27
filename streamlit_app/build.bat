@echo off
REM ClipStream Build Script for Windows
REM This script builds a standalone Windows executable

echo ========================================
echo ClipStream Windows Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Get the directory of this script
cd /d "%~dp0"

echo Step 1: Installing PyInstaller and dependencies...
pip install -q pyinstaller>=6.0.0
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo Step 2: Checking for ffmpeg.exe...
if not exist "ffmpeg.exe" (
    echo WARNING: ffmpeg.exe not found!
    echo.
    echo Please download ffmpeg.exe and place it in this folder.
    echo.
    echo Download link: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
    echo.
    echo Extract the zip and copy ffmpeg.exe to: %cd%
    echo.
    pause
    exit /b 1
)
echo Found ffmpeg.exe

echo.
echo Step 3: Building executable with PyInstaller...
echo This may take a few minutes...
echo.

pyinstaller build_exe.py --clean

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo Your executable is ready at:
echo dist\ClipStream\ClipStream.exe
echo.
echo You can copy the entire dist\ClipStream folder
echo to any Windows computer and run it!
echo.
echo To run: double-click ClipStream.exe
echo.
pause
