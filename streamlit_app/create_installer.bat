@echo off
REM ClipStream Installer Builder
REM This script compiles the Inno Setup installer

echo ============================================
echo ClipStream Installer Builder
echo ============================================
echo.

REM Check if Inno Setup is installed
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files\Inno Setup 5\ISCC.exe"

if not exist %ISCC% (
    echo ERROR: Inno Setup not found!
    echo.
    echo Please install Inno Setup from:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Found Inno Setup Compiler at:
echo %ISCC%
echo.

REM Check for required files
echo Checking required files...

if not exist "app.py" (
    echo ERROR: app.py not found!
    pause
    exit /b 1
)

if not exist "ffmpeg.exe" (
    echo WARNING: ffmpeg.exe not found!
    echo.
    echo Please download ffmpeg.exe and place it in this folder.
    echo Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
    echo.
    pause
    exit /b 1
)

echo All required files found.
echo.

REM Build the installer
echo Building installer...
echo.

%ISCC% installer_script.iss

if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo SUCCESS!
echo ============================================
echo.
echo Installer created at: installer_output\ClipStream-Setup.exe
echo.
echo You can now distribute this installer to users.
echo Users need Python 3.9+ installed to run ClipStream.
echo.
pause
