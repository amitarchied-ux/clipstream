# Creating a ClipStream Windows Installer

This guide explains how to create a Windows installer (.exe) for ClipStream.

## What This Creates

An installer (Setup.exe) that:
- Users download and run on any Windows 10/11 computer
- Checks if Python is installed (prompts to download if not)
- Installs all Python dependencies automatically
- Creates a desktop shortcut
- Adds to Start Menu
- Can be uninstalled cleanly

## Prerequisites

1. **Inno Setup** (Free software for creating installers)
   - Download from: https://jrsoftware.org/isdl.php
   - Install with default settings

2. **FFmpeg executable**
   - Download: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
   - Extract and copy `ffmpeg.exe` to this folder

3. **Project files** (already present)
   - app.py, config.py, utils.py, clipper.py
   - requirements.txt
   - launcher.py

## Build the Installer

### Option 1: Using the batch file (Recommended)

1. Double-click `create_installer.bat`
2. The script will:
   - Check for Inno Setup
   - Verify all required files
   - Build the installer

### Option 2: Manual build with Inno Setup

1. Open Inno Setup Compiler
2. File → Open Script → Select `installer_script.iss`
3. Build → Compile (or press F9)

## Output

After successful build:
```
installer_output/
└── ClipStream-Setup.exe  (~5-10 MB)
```

This is the file you distribute to users!

## User Installation Flow

When a user runs `ClipStream-Setup.exe`:

1. **Welcome screen** - Click Next
2. **License** (optional) - Click Next
3. **Destination folder** - Default: `C:\Program Files\ClipStream`
4. **Start Menu folder** - Click Next
5. **Additional tasks** - Choose desktop shortcut
6. **Python check** - Installer verifies Python is installed
   - If not found: Prompts to download from python.org
7. **Installing files** - Copies app files
8. **Installing dependencies** - Runs `pip install -r requirements.txt`
9. **Finish** - Option to launch ClipStream immediately

## Distribution

Share the installer via:
- **Email attachment** (if small enough)
- **Download link** (Google Drive, Dropbox, etc.)
- **USB drive**
- **GitHub Releases**

## User Requirements

Users need:
- Windows 10 or 11
- Python 3.9 or later (installer will check and prompt)
- Internet connection (for first-run dependency installation)

## After Installation

Users can launch ClipStream by:
- **Desktop shortcut** - Double-click the ClipStream icon
- **Start Menu** - Start → ClipStream → ClipStream
- **Installation folder** - Run `ClipStream.bat`

The app will:
1. Open a console window
2. Automatically open the browser at http://localhost:8501
3. Display the ClipStream interface

## Uninstallation

Users can uninstall:
- **Settings** → Apps → Installed Apps → ClipStream → Uninstall
- Or: Start Menu → ClipStream → Uninstall ClipStream

## Customization

### Change installer icon

Add an `.ico` file to this folder:
1. Create or download an icon (app_icon.ico)
2. Place it in the same folder as installer_script.iss
3. Rebuild the installer

### Change version number

Edit `installer_script.iss`:
```iss
#define AppVersion "1.0.0"  ; Change this
```

### Add a license agreement

1. Create a `LICENSE.txt` file
2. Uncomment this line in installer_script.iss:
```iss
LicenseFile=LICENSE.txt
```

### Include additional files

Add to the `[Files]` section in installer_script.iss:
```iss
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
```

## Troubleshooting

### "Inno Setup not found"

Download and install Inno Setup from https://jrsoftware.org/isdl.php

### "ffmpeg.exe not found"

Download from https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
Extract and copy `ffmpeg.exe` from the `bin/` folder

### Installer compiles but doesn't run

Check Windows Defender or antivirus is not blocking the installer
May need to add an exception

### Dependencies fail to install

User's Python installation may have issues
They can run manually:
```bash
pip install -r "C:\Program Files\ClipStream\requirements.txt"
```

## Advanced: Silent Installation

For enterprise deployment, the installer supports silent mode:
```bash
ClipStream-Setup.exe /VERYSILENT /SUPPRESSMSGBOXES
```

This installs without any user prompts.
