@echo off
REM ClipStream Launcher
REM This batch file starts the ClipStream application

TITLE ClipStream - YouTube Video Clipper

REM Get the directory where this batch file is located
set APP_DIR=%~dp0

REM Set FFmpeg path
set FFMPEG_PATH=%APP_DIR%ffmpeg.exe

REM Set temp directory
set CLIPSTREAM_TEMP_DIR=%APP_DIR%temp

REM Create temp directory if it doesn't exist
if not exist "%CLIPSTREAM_TEMP_DIR%" mkdir "%CLIPSTREAM_TEMP_DIR%"

REM Change to app directory
cd /d "%APP_DIR%"

echo ============================================
echo   ClipStream - YouTube Video Clipper
echo ============================================
echo.
echo Starting ClipStream...
echo.
echo The app will open in your browser automatically.
echo Close this window to stop ClipStream.
echo.
echo ============================================
echo.

REM Launch Streamlit
python -m streamlit run app.py --server.port 8501 --server.headless true

REM If Streamlit exits, pause to show any errors
if errorlevel 1 (
    echo.
    echo An error occurred while running ClipStream.
    echo.
    pause
)
