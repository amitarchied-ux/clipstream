# Building ClipStream Windows Executable

This guide explains how to build a standalone Windows executable (.exe) for ClipStream.

## Prerequisites

1. **Python 3.9+** installed on your Windows computer
2. **Git** (optional, for cloning the repo)

## Step-by-Step Build Process

### 1. Download FFmpeg

The Windows build requires `ffmpeg.exe` to be bundled with the application.

1. Go to: https://www.gyan.dev/ffmpeg/builds/
2. Download: `ffmpeg-release-essentials.zip`
3. Extract the zip file
4. Copy `ffmpeg.exe` from the `bin` folder
5. Paste it into: `streamlit_app/` folder (same folder as `app.py`)

**Direct download link:** https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

### 2. Install Dependencies

Open Command Prompt in the `streamlit_app/` folder and run:

```bash
pip install -r requirements.txt
```

This will install PyInstaller and all other dependencies.

### 3. Build the Executable

**Option A: Using the batch file (Recommended)**

Simply double-click `build.bat` and follow the prompts.

**Option B: Manual build**

```bash
pyinstaller build_exe.py --clean
```

### 4. Locate the Output

After successful build, you'll find:

```
dist/
└── ClipStream/
    ├── ClipStream.exe    <-- Main executable
    ├── ffmpeg.exe        <-- Bundled FFmpeg
    ├── app.py            <-- App modules
    ├── _internal/        <-- Python runtime & dependencies
    └── temp/             <-- Created at runtime
```

## Using the Executable

1. Copy the entire `dist/ClipStream/` folder to any Windows computer
2. Double-click `ClipStream.exe`
3. The app will:
   - Start a local web server
   - Automatically open your default browser
   - Display the ClipStream interface

**No Python installation required on the target computer!**

## Sharing the App

You can share the app via:
- **USB drive** - Copy the `ClipStream` folder
- **Download** - Zip the folder and host for download
- **Network share** - Place on a shared network folder

## Troubleshooting

### Build fails with "ffmpeg.exe not found"

Make sure `ffmpeg.exe` is in the `streamlit_app/` folder, not in a subfolder.

### Antivirus blocks the executable

Some antivirus software may flag PyInstaller-built executables as false positives.
You may need to add an exception for the executable.

### Browser doesn't open automatically

1. Check if a firewall is blocking the connection
2. Manually open: http://localhost:8501

### "Port 8501 already in use"

Edit `launcher.py` and change `STREAMLIT_PORT = 8501` to a different port.

## File Size

The final executable will be approximately **100-200 MB** because it includes:
- Python interpreter
- All dependencies (Streamlit, yt-dlp, etc.)
- FFmpeg executable

## Advanced: Single File Mode

To create a true single-file executable (slower startup), edit `build_exe.py`:

Change the EXE section to include `exclude_binaries=False` and remove the COLLECT section.

Note: Single-file mode extracts all files to a temp folder on each run, which is slower.

## Uninstallation

To remove the app:
1. Close `ClipStream.exe` if running
2. Delete the `ClipStream` folder
3. Delete `temp/clipstream` from your temp directory (if exists)
