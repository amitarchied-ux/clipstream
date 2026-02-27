"""
Configuration Module

Centralized configuration for the YouTube clipper application.
"""

import os
import tempfile
from pathlib import Path
from datetime import timedelta


# ============================================================================
# PATHS AND DIRECTORIES
# ============================================================================

# Base directory (auto-detected)
BASE_DIR = Path(__file__).parent.absolute()

# Temporary directory for file processing
TEMP_DIR = os.environ.get(
    'CLIPSTREAM_TEMP_DIR',
    os.path.join(tempfile.gettempdir(), 'clipstream')
)

# FFmpeg executable path (set if not in PATH)
FFMPEG_PATH = os.environ.get('FFMPEG_PATH', None)

# FFprobe executable path (for media info)
FFPROBE_PATH = os.environ.get('FFPROBE_PATH', None)


# ============================================================================
# CLIP PROCESSING LIMITS
# ============================================================================

# Maximum clip duration in seconds (30 minutes default)
MAX_CLIP_DURATION = int(os.environ.get('CLIPSTREAM_MAX_DURATION', '1800'))

# Minimum clip duration in seconds
MIN_CLIP_DURATION = int(os.environ.get('CLIPSTREAM_MIN_DURATION', '1'))

# Maximum file size in bytes (500 MB default)
MAX_FILE_SIZE = int(os.environ.get('CLIPSTREAM_MAX_FILE_SIZE', str(500 * 1024 * 1024)))


# ============================================================================
# SUPPORTED FORMATS AND QUALITY
# ============================================================================

SUPPORTED_FORMATS = {
    'video': ['mp4', 'webm', 'mkv'],
    'audio': ['mp3', 'm4a', 'aac', 'opus', 'wav']
}

DEFAULT_VIDEO_FORMAT = 'mp4'
DEFAULT_AUDIO_FORMAT = 'mp3'

# Quality presets for different formats
QUALITY_PRESETS = {
    'mp4': {
        'video_codec': 'libx264',
        'audio_codec': 'aac',
        'video_bitrate': 'copy',  # Copy original (fast)
        'audio_bitrate': 'copy',
        'extension': 'mp4'
    },
    'mp3': {
        'audio_codec': 'libmp3lame',
        'audio_bitrate': '192k',
        'quality': '2',  # 0-9, lower is better
        'extension': 'mp3'
    },
    'm4a': {
        'audio_codec': 'aac',
        'audio_bitrate': '192k',
        'extension': 'm4a'
    }
}


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

# Session timeout before cleanup
SESSION_TIMEOUT = timedelta(minutes=int(os.environ.get('CLIPSTREAM_SESSION_TIMEOUT', '30')))

# Maximum number of concurrent sessions
MAX_CONCURRENT_SESSIONS = int(os.environ.get('CLIPSTREAM_MAX_SESSIONS', '50'))


# ============================================================================
# CLEANUP SETTINGS
# ============================================================================

# How often to run cleanup (in seconds)
CLEANUP_INTERVAL = int(os.environ.get('CLIPSTREAM_CLEANUP_INTERVAL', '300'))

# Maximum age of temp files before cleanup (in hours)
TEMP_FILE_MAX_AGE = int(os.environ.get('CLIPSTREAM_TEMP_MAX_AGE', '1'))

# Whether to cleanup after download
CLEANUP_AFTER_DOWNLOAD = os.environ.get('CLIPSTREAM_CLEANUP_AFTER_DOWNLOAD', 'true').lower() == 'true'


# ============================================================================
# YT-DLP CONFIGURATION
# ============================================================================

YDLP_OPTIONS = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'nocheckcertificate': True,
    'socket_timeout': 30,
    # User agent to avoid blocking
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    # Retry settings
    'retries': 3,
    'fragment_retries': 3,
    # Buffer size
    'buffersize': 1024 * 16,
}


# ============================================================================
# UI CONFIGURATION
# ============================================================================

UI_CONFIG = {
    'title': 'ClipStream',
    'tagline': 'Premium YouTube Clipper',
    'favicon': '🎬',

    # Color scheme (no purple/blue as per requirements)
    'colors': {
        'primary': '#10b981',      # Emerald green
        'primary_dark': '#059669',
        'primary_light': '#34d399',
        'secondary': '#f59e0b',    # Gold/amber
        'accent': '#b45309',       # Copper
        'background': '#1a1a1a',   # Dark charcoal
        'surface': '#2d2d2d',      # Lighter charcoal
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'info': '#3b82f6',
    },

    # Timestamp format suggestions
    'timestamp_examples': [
        '1:30',      # 1 minute 30 seconds
        '01:30',     # Same, with leading zero
        '1:30:45',   # 1 hour 30 minutes 45 seconds
        '90',        # 90 seconds
    ],

    # Default values
    'default_start': '00:00',
    'default_end': '01:00',
    'default_format': 'mp4',
}


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.environ.get('CLIPSTREAM_LOG_LEVEL', 'INFO')

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Log file path (None for stdout only)
LOG_FILE = os.environ.get('CLIPSTREAM_LOG_FILE', None)


# ============================================================================
# RATE LIMITING
# ============================================================================

# Requests per minute per IP
RATE_LIMIT_PER_MINUTE = int(os.environ.get('CLIPSTREAM_RATE_LIMIT', '10'))

# Requests per hour per IP
RATE_LIMIT_PER_HOUR = int(os.environ.get('CLIPSTREAM_RATE_LIMIT_HOUR', '30'))


# ============================================================================
# STREAMLIT-SPECIFIC CONFIG
# ============================================================================

# These are set via st.set_page_config, but stored here for reference
STREAMLIT_PAGE_CONFIG = {
    'page_title': UI_CONFIG['title'] + ' | YouTube Clipper',
    'page_icon': UI_CONFIG['favicon'],
    'layout': 'centered',
    'initial_sidebar_state': 'collapsed',
}


# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================

def is_development() -> bool:
    """Check if running in development environment."""
    return os.environ.get('CLIPSTREAM_ENV', 'production').lower() == 'development'


def is_production() -> bool:
    """Check if running in production environment."""
    return not is_development()


def is_vercel() -> bool:
    """Check if running on Vercel."""
    return os.environ.get('VERCEL') == '1'


def is_streamlit_cloud() -> bool:
    """Check if running on Streamlit Community Cloud."""
    return os.environ.get('STREAMLIT_SHARING_BASE_URL') is not None


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_config() -> list:
    """
    Validate configuration settings.

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check temp directory is writable
    try:
        os.makedirs(TEMP_DIR, exist_ok=True)
        test_file = os.path.join(TEMP_DIR, 'test_write')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
    except Exception as e:
        errors.append(f"Cannot write to temp directory {TEMP_DIR}: {e}")

    # Check FFmpeg is available
    import shutil
    ffmpeg_path = FFMPEG_PATH or 'ffmpeg'
    if not shutil.which(ffmpeg_path):
        errors.append(f"FFmpeg not found at {ffmpeg_path}")

    # Validate limits
    if MAX_CLIP_DURATION < MIN_CLIP_DURATION:
        errors.append("MAX_CLIP_DURATION must be greater than MIN_CLIP_DURATION")

    if MAX_CLIP_DURATION > 14400:  # 4 hours
        errors.append("MAX_CLIP_DURATION exceeds 4 hours")

    return errors


# ============================================================================
# DEPLOYMENT-SPECIFIC OVERRIDES
# ============================================================================

def apply_environment_overrides():
    """Apply environment-specific configuration overrides."""
    if is_vercel():
        # Vercel-specific overrides
        global TEMP_DIR, MAX_CLIP_DURATION
        TEMP_DIR = '/tmp/clipstream'
        MAX_CLIP_DURATION = min(MAX_CLIP_DURATION, 600)  # 10 minutes max for serverless


# Apply overrides on import
apply_environment_overrides()
