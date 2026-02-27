"""
Utility Functions Module

Common utility functions used across the application.
"""

import os
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple

from config import TEMP_DIR


# ============================================================================
# TIMESTAMP PARSING AND FORMATTING
# ============================================================================

def parse_timestamp(timestamp: str) -> float:
    """
    Parse timestamp string to seconds.

    Supports formats:
    - MM:SS (e.g., "1:30", "01:30")
    - HH:MM:SS (e.g., "1:30:45", "01:30:45")
    - Seconds only (e.g., "90")

    Args:
        timestamp: Timestamp string

    Returns:
        Time in seconds as float

    Raises:
        ValueError: If timestamp format is invalid
    """
    timestamp = timestamp.strip()

    # Try HH:MM:SS format
    hms_match = re.match(r'^(\d+):(\d{2}):(\d{2})$', timestamp)
    if hms_match:
        hours, minutes, seconds = hms_match.groups()
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)

    # Try MM:SS format
    ms_match = re.match(r'^(\d+):(\d{2})$', timestamp)
    if ms_match:
        minutes, seconds = ms_match.groups()
        return int(minutes) * 60 + int(seconds)

    # Try seconds only
    seconds_match = re.match(r'^(\d+(?:\.\d+)?)$', timestamp)
    if seconds_match:
        return float(seconds_match.group(1))

    raise ValueError(
        f"Invalid timestamp format: '{timestamp}'. "
        "Use MM:SS, HH:MM:SS, or seconds."
    )


def format_timestamp(seconds: float) -> str:
    """
    Format seconds to timestamp string.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string (HH:MM:SS or MM:SS)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def calculate_duration(start: float, end: float) -> float:
    """
    Calculate duration between two timestamps.

    Args:
        start: Start time in seconds
        end: End time in seconds

    Returns:
        Duration in seconds

    Raises:
        ValueError: If duration is negative
    """
    duration = end - start
    if duration < 0:
        raise ValueError("End time must be after start time")
    return duration


# ============================================================================
# URL VALIDATION
# ============================================================================

def validate_url(url: str) -> bool:
    """
    Validate YouTube URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid YouTube URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()

    # YouTube URL patterns
    patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'https?://youtu\.be/[\w-]+',
        r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
        r'https?://(?:www\.)?youtube\.com/v/[\w-]+',
        r'https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
    ]

    return any(re.match(pattern, url) for pattern in patterns)


def extract_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL.

    Args:
        url: YouTube URL

    Returns:
        Video ID string

    Raises:
        ValueError: If URL is invalid or video ID cannot be extracted
    """
    patterns = {
        'watch': r'[?&]v=([^&]+)',
        'shorts': r'/shorts/([^/?]+)',
        'embed': r'/embed/([^/?]+)',
        'v': r'/v/([^/?]+)',
        'youtu.be': r'youtu\.be/([^/?]+)',
    }

    for pattern_type, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from URL: {url}")


# ============================================================================
# FILENAME SANITIZATION
# ============================================================================

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename for safe filesystem usage.

    Removes/replaces characters that are problematic on various filesystems.

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        Sanitized filename
    """
    # Remove/replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    filename = filename.strip()

    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)

    # Limit length
    if len(filename) > max_length:
        filename = filename[:max_length].rsplit(' ', 1)[0]

    # Ensure filename is not empty
    if not filename:
        filename = "clip"

    return filename


def get_file_extension(format_type: str) -> str:
    """
    Get file extension for format type.

    Args:
        format_type: Format type (mp4, mp3, etc.)

    Returns:
        File extension with dot (e.g., ".mp4")
    """
    return f".{format_type.lower().lstrip('.')}"


# ============================================================================
# FILE SIZE FORMATTING
# ============================================================================

def format_file_size(bytes_size: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def format_bitrate(bps: float) -> str:
    """
    Format bitrate in human-readable format.

    Args:
        bps: Bits per second

    Returns:
        Formatted bitrate string (e.g., "1.5 Mbps")
    """
    for unit, threshold in [('bps', 1000), ('Kbps', 1000000), ('Mbps', 1000000000)]:
        if bps < threshold:
            return f"{bps / (threshold / 1000):.2f} {unit}"
    return f"{bps / 1000000000:.2f} Gbps"


# ============================================================================
# FILE CLEANUP
# ============================================================================

def cleanup_old_files(directory: str, max_age_hours: int = 1) -> int:
    """
    Clean up old files from directory.

    Args:
        directory: Directory to clean
        max_age_hours: Maximum file age in hours

    Returns:
        Number of files deleted
    """
    if not os.path.exists(directory):
        return 0

    deleted_count = 0
    cutoff_time = time.time() - (max_age_hours * 3600)

    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            # Only delete files, not directories
            if os.path.isfile(file_path):
                file_age = os.path.getmtime(file_path)

                if file_age < cutoff_time:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except OSError as e:
                        # Log but continue with other files
                        print(f"Warning: Could not delete {file_path}: {e}")

    except OSError as e:
        print(f"Warning: Could not access directory {directory}: {e}")

    return deleted_count


def cleanup_file(file_path: str) -> bool:
    """
    Clean up a single file.

    Args:
        file_path: Path to file to delete

    Returns:
        True if file was deleted, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except OSError:
        pass
    return False


# ============================================================================
# PROGRESS TRACKING
# ============================================================================

class ProgressTracker:
    """Track progress of long-running operations."""

    def __init__(self, total_steps: int = 100):
        """
        Initialize progress tracker.

        Args:
            total_steps: Total number of steps
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()

    def update(self, steps: int = 1) -> float:
        """
        Update progress.

        Args:
            steps: Number of steps to increment

        Returns:
            Progress as fraction (0-1)
        """
        self.current_step = min(self.current_step + steps, self.total_steps)
        return self.get_progress()

    def get_progress(self) -> float:
        """
        Get current progress.

        Returns:
            Progress as fraction (0-1)
        """
        return self.current_step / self.total_steps if self.total_steps > 0 else 0

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since start.

        Returns:
            Elapsed time in seconds
        """
        return time.time() - self.start_time

    def get_estimated_remaining(self) -> float:
        """
        Estimate remaining time.

        Returns:
            Estimated remaining time in seconds
        """
        progress = self.get_progress()
        if progress > 0:
            elapsed = self.get_elapsed_time()
            return (elapsed / progress) - elapsed
        return 0


# ============================================================================
# TIMEZONE HELPER
# ============================================================================

def get_current_timestamp() -> str:
    """
    Get current timestamp as string.

    Returns:
        ISO format timestamp string
    """
    return datetime.now().isoformat()


def parse_iso_timestamp(timestamp: str) -> datetime:
    """
    Parse ISO format timestamp.

    Args:
        timestamp: ISO format timestamp string

    Returns:
        datetime object
    """
    return datetime.fromisoformat(timestamp)
