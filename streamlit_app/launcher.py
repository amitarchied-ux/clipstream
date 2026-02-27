"""
ClipStream Launcher

This script launches the Streamlit app when the executable is run.
It's used as the entry point for the PyInstaller-built executable.

Usage (as exe):
    ClipStream.exe

The executable will:
1. Start a local Streamlit server
2. Automatically open the default web browser
3. Display the ClipStream UI
"""

import sys
import os
import time
import subprocess
import webbrowser
from pathlib import Path

# Configuration
STREAMLIT_PORT = 8501
STREAMLIT_HOST = 'localhost'
APP_URL = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"

# Setup paths
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    BUNDLE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BUNDLE_DIR = Path(__file__).parent

# Set up FFmpeg path if bundled
ffmpeg_path = BUNDLE_DIR / "ffmpeg.exe"
if ffmpeg_path.exists():
    os.environ['FFMPEG_PATH'] = str(ffmpeg_path)

# Set temp directory for bundled app
temp_dir = BUNDLE_DIR / "temp"
temp_dir.mkdir(exist_ok=True)
os.environ['CLIPSTREAM_TEMP_DIR'] = str(temp_dir)


def wait_for_server(url: str, max_wait: int = 30) -> bool:
    """Wait for Streamlit server to be ready."""
    import urllib.request
    import urllib.error

    for _ in range(max_wait * 2):  # Check twice per second
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def main():
    """Main entry point for the bundled application."""

    print("=" * 50)
    print("ClipStream - YouTube Video Clipper")
    print("=" * 50)
    print()
    print("Starting Streamlit server...")
    print(f"Server will run at: {APP_URL}")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    print()

    # Determine app.py location
    if getattr(sys, 'frozen', False):
        # When bundled, app.py should be in the bundle directory
        app_py = BUNDLE_DIR / "app.py"
    else:
        app_py = BUNDLE_DIR / "app.py"

    # Verify app.py exists
    if not app_py.exists():
        print(f"ERROR: Could not find app.py at {app_py}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Open browser after a short delay
    def open_browser_later():
        time.sleep(3)  # Give server time to start
        if wait_for_server(APP_URL):
            print(f"\nServer is ready! Opening browser...")
            webbrowser.open(APP_URL)
        else:
            print(f"\nCould not connect to server. Please open manually: {APP_URL}")

    import threading
    browser_thread = threading.Thread(target=open_browser_later, daemon=True)
    browser_thread.start()

    # Build Streamlit command
    streamlit_cmd = [
        sys.executable,
        '-m', 'streamlit',
        'run',
        str(app_py),
        '--server.port', str(STREAMLIT_PORT),
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false',
    ]

    # Launch Streamlit
    try:
        subprocess.run(streamlit_cmd)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError running Streamlit: {e}")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == '__main__':
    main()
