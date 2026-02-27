"""
YouTube Video Clipper - Production-Ready Streamlit Application
Efficiently clips YouTube videos without downloading the full file.

Architecture:
- Streamlit UI layer (this file)
- Processing layer (clipper.py)
- Utilities layer (utils.py)
- Configuration layer (config.py)

Deployment Options:
- Streamlit Community Cloud: https://streamlit.io/cloud
- Railway, Fly.io, Render, or any container platform
"""

import streamlit as st
import time
from pathlib import Path
import tempfile
import os
from datetime import datetime, timedelta

# Import application modules
from clipper import YouTubeClipper, ClipProcessingError
from utils import (
    parse_timestamp,
    format_timestamp,
    validate_url,
    calculate_duration,
    sanitize_filename,
    cleanup_old_files
)
from config import (
    MAX_CLIP_DURATION,
    TEMP_DIR,
    SUPPORTED_FORMATS,
    SESSION_TIMEOUT,
    UI_CONFIG
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="ClipStream | Premium YouTube Clipper",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM CSS - Premium Styling (No Purple/Blue)
# ============================================================================

st.markdown("""
<style>
    :root {
        --primary-dark: #1a1a1a;
        --primary-charcoal: #2d2d2d;
        --emerald-primary: #10b981;
        --emerald-dark: #059669;
        --emerald-light: #34d399;
        --gold-accent: #f59e0b;
        --copper: #b45309;
        --slate-800: #1e293b;
        --slate-700: #334155;
        --slate-600: #475569;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
    }

    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, var(--primary-dark) 0%, #0f0f0f 100%);
    }

    /* Header Styles */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem;
        border-bottom: 1px solid var(--primary-charcoal);
        margin-bottom: 2rem;
    }

    .main-header h1 {
        color: var(--text-primary) !important;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }

    .main-header .subtitle {
        color: var(--text-muted);
        font-size: 1rem;
        font-weight: 400;
    }

    .main-header .accent {
        color: var(--emerald-primary);
    }

    /* Container Cards */
    .input-card {
        background: var(--primary-charcoal);
        border: 1px solid var(--slate-700);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* Input Styles */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: var(--slate-800);
        color: var(--text-primary);
        border: 1px solid var(--slate-600);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--emerald-primary);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        outline: none;
    }

    /* Label Styles */
    .stTextInput label,
    .stSelectbox label {
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, var(--emerald-primary) 0%, var(--emerald-dark) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Download Button */
    .download-btn {
        background: linear-gradient(135deg, var(--gold-accent) 0%, var(--copper) 100%) !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3) !important;
    }

    .download-btn:hover {
        box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4) !important;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--emerald-primary) 0%, var(--emerald-light) 100%);
    }

    /* Success/Info/Error Messages */
    .success-message {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid var(--emerald-primary);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        color: var(--emerald-light);
    }

    .error-message {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        color: #fca5a5;
    }

    .info-message {
        background: rgba(16, 185, 129, 0.05);
        border: 1px solid var(--slate-600);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        color: var(--text-secondary);
    }

    /* Timestamp Input Group */
    .timestamp-group {
        display: flex;
        gap: 1rem;
        align-items: flex-end;
    }

    .timestamp-field {
        flex: 1;
    }

    /* Format Selector */
    .format-selector {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
    }

    .format-option {
        flex: 1;
        text-align: center;
        padding: 0.75rem;
        background: var(--slate-800);
        border: 2px solid var(--slate-600);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .format-option:hover {
        border-color: var(--emerald-primary);
    }

    .format-option.selected {
        border-color: var(--emerald-primary);
        background: rgba(16, 185, 129, 0.1);
    }

    /* Video Info Display */
    .video-info {
        background: var(--slate-800);
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }

    .video-info-title {
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .video-info-meta {
        color: var(--text-muted);
        font-size: 0.9rem;
        display: flex;
        gap: 1rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: var(--text-muted);
        font-size: 0.85rem;
        border-top: 1px solid var(--primary-charcoal);
        margin-top: 3rem;
    }

    /* Hide streamlit footer */
    footer {visibility: hidden;}
    .footer {visibility: visible;}

    /* Hide main menu */
    #MainMenu {visibility: hidden;}

    /* Status indicators */
    .status-processing {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--emerald-primary);
        font-weight: 600;
    }

    .spinner {
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'clip_path' not in st.session_state:
        st.session_state.clip_path = None
    if 'video_info' not in st.session_state:
        st.session_state.video_info = None
    if 'error' not in st.session_state:
        st.session_state.error = None
    if 'success' not in st.session_state:
        st.session_state.success = None
    if 'temp_files' not in st.session_state:
        st.session_state.temp_files = []
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()

init_session_state()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def display_header():
    """Display the application header."""
    st.markdown("""
    <div class="main-header">
        <h1>ClipStream</h1>
        <p class="subtitle">Premium YouTube Video <span class="accent">Clipper</span></p>
    </div>
    """, unsafe_allow_html=True)

def display_info_message(message: str):
    """Display an info message."""
    st.markdown(f'<div class="info-message">{message}</div>', unsafe_allow_html=True)

def display_success_message(message: str):
    """Display a success message."""
    st.markdown(f'<div class="success-message">✓ {message}</div>', unsafe_allow_html=True)

def display_error_message(message: str):
    """Display an error message."""
    st.markdown(f'<div class="error-message">⚠ {message}</div>', unsafe_allow_html=True)

def cleanup_session_files():
    """Clean up temporary files from current session."""
    if st.session_state.temp_files:
        for file_path in st.session_state.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        st.session_state.temp_files = []

def check_session_timeout():
    """Check if session has timed out and cleanup if needed."""
    session_age = datetime.now() - st.session_state.session_start
    if session_age > SESSION_TIMEOUT:
        cleanup_session_files()
        st.session_state.session_start = datetime.now()
        st.session_state.clip_path = None

# Run session cleanup
check_session_timeout()
cleanup_old_files(TEMP_DIR, max_age_hours=1)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

display_header()

# Main container
with st.container():
    # Input Section
    st.markdown('<div class="input-card">', unsafe_allow_html=True)

    # YouTube URL Input
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown('<span style="font-size: 1.5rem;">🔗</span>', unsafe_allow_html=True)
    with col2:
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
            key="youtube_url_input"
        )

    # Timestamp Inputs
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.text_input(
            "Start Time",
            placeholder="MM:SS or HH:MM:SS",
            value="00:00",
            key="start_time_input"
        )
    with col2:
        end_time = st.text_input(
            "End Time",
            placeholder="MM:SS or HH:MM:SS",
            value="01:00",
            key="end_time_input"
        )

    # Format Selection
    output_format = st.selectbox(
        "Output Format",
        options=["MP4 (Video)", "MP3 (Audio Only)"],
        index=0,
        key="format_selector"
    )
    format_ext = "mp4" if "MP4" in output_format else "mp3"

    st.markdown('</div>', unsafe_allow_html=True)

    # Validation Section
    if youtube_url:
        try:
            if not validate_url(youtube_url):
                display_error_message("Please enter a valid YouTube URL")
                st.stop()

            # Get video info
            with st.spinner("Fetching video information..."):
                clipper = YouTubeClipper(youtube_url)
                video_info = clipper.get_video_info()

            if video_info:
                st.session_state.video_info = video_info

                # Display video info
                st.markdown("""
                <div class="video-info">
                    <div class="video-info-title">{title}</div>
                    <div class="video-info-meta">
                        <span>Duration: {duration}</span>
                        <span>Channel: {channel}</span>
                    </div>
                </div>
                """.format(
                    title=video_info.get('title', 'Unknown'),
                    duration=format_timestamp(video_info.get('duration', 0)),
                    channel=video_info.get('channel', 'Unknown')
                ), unsafe_allow_html=True)

                # Parse and validate timestamps
                try:
                    start_seconds = parse_timestamp(start_time)
                    end_seconds = parse_timestamp(end_time)
                    duration = calculate_duration(start_seconds, end_seconds)
                    video_duration = video_info.get('duration', 0)

                    if start_seconds >= video_duration:
                        display_error_message(f"Start time exceeds video duration ({format_timestamp(video_duration)})")
                        st.stop()

                    if end_seconds > video_duration:
                        display_error_message(f"End time exceeds video duration ({format_timestamp(video_duration)})")
                        st.stop()

                    if duration <= 0:
                        display_error_message("End time must be after start time")
                        st.stop()

                    if duration > MAX_CLIP_DURATION:
                        display_error_message(f"Clip duration exceeds maximum of {MAX_CLIP_DURATION//60} minutes")
                        st.stop()

                    # Display clip info
                    display_info_message(
                        f"📺 Clip Duration: {format_timestamp(duration)} | "
                        f"From {start_time} to {end_time}"
                    )

                except ValueError as e:
                    display_error_message(f"Invalid timestamp format: {str(e)}")
                    st.stop()

        except Exception as e:
            display_error_message(f"Error fetching video: {str(e)}")
            st.stop()

    # Process Button
    process_clicked = st.button(
        "🎬 Generate Clip",
        use_container_width=True,
        disabled=st.session_state.processing or not youtube_url
    )

    # Processing Section
    if process_clicked and youtube_url:
        st.session_state.processing = True
        st.session_state.error = None
        st.session_state.success = None
        st.session_state.clip_path = None

        try:
            # Clear previous clips
            cleanup_session_files()

            # Create progress bar
            progress_bar = st.progress(0, text="Initializing...")
            status_text = st.empty()

            # Parse timestamps
            start_seconds = parse_timestamp(start_time)
            end_seconds = parse_timestamp(end_time)
            duration = calculate_duration(start_seconds, end_seconds)

            # Initialize clipper
            progress_bar.progress(10, text="Initializing clipper...")
            status_text.text("Preparing to extract stream...")

            clipper = YouTubeClipper(youtube_url)

            # Process the clip
            progress_bar.progress(20, text="Extracting video stream...")
            status_text.text("Downloading and processing clip...")

            clip_path = clipper.create_clip(
                start_time=start_seconds,
                end_time=end_seconds,
                output_format=format_ext,
                progress_callback=lambda p: progress_bar.progress(
                    20 + int(p * 70),
                    text=f"Processing: {int(p * 100)}%"
                )
            )

            if clip_path and os.path.exists(clip_path):
                progress_bar.progress(100, text="Complete!")
                status_text.text("Clip ready for download!")

                st.session_state.clip_path = clip_path
                st.session_state.temp_files.append(clip_path)

                # Get file size
                file_size = os.path.getsize(clip_path)
                file_size_mb = file_size / (1024 * 1024)

                display_success_message(
                    f"Clip created successfully! Size: {file_size_mb:.2f} MB"
                )

            else:
                raise Exception("Failed to create clip file")

        except ClipProcessingError as e:
            st.session_state.error = str(e)
            display_error_message(f"Processing error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

        except Exception as e:
            st.session_state.error = str(e)
            display_error_message(f"Unexpected error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

        finally:
            st.session_state.processing = False

    # Download Section
    if st.session_state.clip_path and os.path.exists(st.session_state.clip_path):
        st.markdown("---")

        # Read file for download
        with open(st.session_state.clip_path, 'rb') as f:
            file_bytes = f.read()

        # Generate filename
        video_title = sanitize_filename(
            st.session_state.video_info.get('title', 'clip')
            if st.session_state.video_info else 'clip'
        )
        filename = f"{video_title}_{start_time.replace(':', '-')}-{end_time.replace(':', '-')}.{format_ext}"

        st.download_button(
            label=f"⬇ Download Clip ({format_ext.upper()})",
            data=file_bytes,
            file_name=filename,
            mime=f"video/{format_ext}" if format_ext == "mp4" else "audio/mpeg",
            use_container_width=True,
            key="download_button",
            on_click=lambda: cleanup_session_files()
        )

        display_info_message(
            "💡 Your clip will be automatically deleted after download."
        )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div class="footer">
    <p>ClipStream | Efficient YouTube Clipping</p>
    <p style="font-size: 0.75rem; margin-top: 0.5rem; color: #64748b;">
        Clips are processed server-side and automatically cleaned up
    </p>
</div>
""", unsafe_allow_html=True)
