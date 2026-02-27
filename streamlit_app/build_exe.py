"""
PyInstaller Build Script for ClipStream Windows Desktop App

This script builds a standalone Windows executable (.exe) that:
- Runs on any Windows computer without Python
- Bundles all dependencies (yt-dlp, ffmpeg-python, streamlit, etc.)
- Includes FFmpeg executable
- Auto-launches Streamlit in browser on run

Usage:
    python build_exe.py

Output:
    dist/ClipStream.exe (~100-200 MB)
"""

import os
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Application name
APP_NAME = "ClipStream"

# Main entry point (launcher script that starts Streamlit)
MAIN_SCRIPT = "launcher.py"

# Streamlit app to bundle
APP_SCRIPT = "app.py"

# FFmpeg executable location
FFMPEG_BIN = Path(__file__).parent / "ffmpeg.exe"

# Icon (optional - add .ico file to root if desired)
ICON_PATH = None  # or "icon.ico" if you have one

# ============================================================================
# PYINSTALLER SPEC
# ============================================================================

block_cipher = None

# Collect all hidden imports (modules imported dynamically)
hidden_imports = [
    'streamlit',
    'streamlit.cli',
    'yt_dlp',
    'ffmpeg',
    'ffmpeg._ffmpeg',
    'pydantic',
    'httpx',
    'aiofiles',
]

# Data files to bundle (ffmpeg.exe + app modules)
datas = []

# Check if ffmpeg.exe exists
if FFMPEG_BIN.exists():
    datas.append((str(FFMPEG_BIN), "."))
    print(f"Found ffmpeg.exe at: {FFMPEG_BIN}")
else:
    print(f"WARNING: ffmpeg.exe not found at {FFMPEG_BIN}")
    print("Please download ffmpeg.exe and place it in the streamlit_app folder")
    print("Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip")
    response = input("Continue anyway? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)

# Add all app modules to bundle
app_modules = ['app.py', 'config.py', 'utils.py', 'clipper.py']
for module in app_modules:
    module_path = Path(__file__).parent / module
    if module_path.exists():
        datas.append((str(module_path), "."))
        print(f"Adding {module} to bundle")

# PyInstaller Analysis configuration
a = Analysis(
    [MAIN_SCRIPT],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary modules to reduce size
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Show console for Streamlit output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

print("\n" + "=" * 50)
print("Build complete!")
print(f"Executable location: dist/{APP_NAME}/{APP_NAME}.exe")
print("=" * 50)
