"""
FFmpeg Download Helper for ClipStream

This script helps download ffmpeg.exe for Windows.
Run this before building the executable.

Usage:
    python download_ffmpeg.py
"""

import urllib.request
import os
from pathlib import Path

# FFmpeg download URL (Windows 64-bit essentials build)
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
DEST_DIR = Path(__file__).parent
FFMPEG_EXE = DEST_DIR / "ffmpeg.exe"

def download_file(url: str, dest_path: Path) -> bool:
    """Download a file with progress indication."""
    try:
        print(f"Downloading from: {url}")
        print(f"Saving to: {dest_path}")

        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = int(downloaded / total_size * 100) if total_size > 0 else 0
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\rProgress: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")

        urllib.request.urlretrieve(url, dest_path, reporthook=report_progress)
        print("\nDownload complete!")
        return True
    except Exception as e:
        print(f"\nError downloading: {e}")
        return False

def main():
    """Main download function."""
    print("=" * 50)
    print("FFmpeg Download Helper for ClipStream")
    print("=" * 50)
    print()

    # Check if already exists
    if FFMPEG_EXE.exists():
        print(f"ffmpeg.exe already exists at: {FFMPEG_EXE}")
        response = input("Download again to overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return

    print("This will download ffmpeg.exe (~100 MB)")
    print()
    print("Note: The download includes a zip file that needs manual extraction.")
    print("For easier setup, please follow these manual steps:")
    print()
    print("1. Download from: " + FFMPEG_URL)
    print("2. Extract the zip file")
    print("3. Copy ffmpeg.exe from the bin/ folder")
    print("4. Paste it into this folder:")
    print(f"   {DEST_DIR}")
    print()
    print("Press Enter to open the download page in your browser...")
    input()

    # Open browser to download page
    import webbrowser
    webbrowser.open(FFMPEG_URL)

    print()
    print("After downloading and extracting ffmpeg.exe, run build.bat to create the executable.")

if __name__ == "__main__":
    main()
