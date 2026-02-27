"""
YouTube Clipper Module - Core Processing Engine

This module handles the efficient extraction of clips from YouTube videos
using stream-based processing to minimize bandwidth and storage.

Key Features:
- Fast seeking using ffmpeg (no re-encoding)
- Stream-based download using yt-dlp
- Memory-efficient processing
- Multiple output format support
"""

import os
import subprocess
import tempfile
import logging
from typing import Optional, Callable
from dataclasses import dataclass

import yt_dlp

from config import (
    TEMP_DIR,
    FFMPEG_PATH,
    MAX_CLIP_DURATION,
    QUALITY_PRESETS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Data class for video information."""
    title: str
    duration: int
    channel: str
    thumbnail: str
    views: int
    upload_date: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'duration': self.duration,
            'channel': self.channel,
            'thumbnail': self.thumbnail,
            'views': self.views,
            'upload_date': self.upload_date
        }


class ClipProcessingError(Exception):
    """Custom exception for clip processing errors."""
    pass


class YouTubeClipper:
    """
    Efficient YouTube video clipper using stream extraction.

    Architecture:
    1. Uses yt-dlp to get direct video stream URLs
    2. Uses ffmpeg with -ss flag for fast seeking (no re-encoding)
    3. Processes clips directly from stream (no full download)

    This approach minimizes:
    - Bandwidth usage (only downloads needed segment + keyframes)
    - Processing time (fast seeking at keyframe boundaries)
    - Storage requirements (only stores the clip)
    """

    # Audio formats for MP3 extraction
    AUDIO_FORMATS = ['m4a', 'aac', 'mp3', 'opus', 'webm']

    # Video formats for MP4 extraction (prioritize compatible formats)
    VIDEO_FORMATS = ['mp4', 'webm']

    def __init__(self, url: str, temp_dir: Optional[str] = None):
        """
        Initialize the YouTube clipper.

        Args:
            url: YouTube video URL
            temp_dir: Temporary directory for processing (default from config)
        """
        self.url = url
        self.temp_dir = temp_dir or TEMP_DIR
        self._ensure_temp_dir()
        self._video_info: Optional[VideoInfo] = None
        self._stream_url: Optional[str] = None
        self._audio_url: Optional[str] = None

    def _ensure_temp_dir(self):
        """Ensure temporary directory exists."""
        os.makedirs(self.temp_dir, exist_ok=True)

    def _build_ydl_options(self, extract_only: bool = True) -> dict:
        """
        Build yt-dlp options.

        Args:
            extract_only: If True, only extract info without downloading

        Returns:
            Dictionary of yt-dlp options
        """
        return {
            'format': 'best',  # Best quality, will be filtered later
            'quiet': True,
            'no_warnings': True,
            'extract_flat': extract_only,
            'nocheckcertificate': True,
            'socket_timeout': 30,
        }

    def get_video_info(self) -> Optional[dict]:
        """
        Fetch video information without downloading.

        Returns:
            Dictionary with video metadata or None on error
        """
        try:
            ydl_opts = self._build_ydl_options(extract_only=False)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

                if info:
                    self._video_info = VideoInfo(
                        title=info.get('title', 'Unknown'),
                        duration=int(info.get('duration', 0)),
                        channel=info.get('channel', 'Unknown'),
                        thumbnail=info.get('thumbnail', ''),
                        views=int(info.get('view_count', 0)),
                        upload_date=info.get('upload_date', '')
                    )

                    # Store stream URLs for later use
                    self._extract_stream_urls(info)

                    return self._video_info.to_dict()

        except Exception as e:
            logger.error(f"Error fetching video info: {e}")
            raise ClipProcessingError(f"Could not fetch video information: {str(e)}")

        return None

    def _extract_stream_urls(self, info: dict) -> None:
        """
        Extract direct stream URLs from video info.

        This method finds the best video and audio streams for efficient
        clip extraction.

        Args:
            info: Video info dictionary from yt-dlp
        """
        formats = info.get('formats', [])

        # Find best video-only stream
        video_formats = [
            f for f in formats
            if f.get('vcodec', 'none') != 'none' and
            f.get('acodec', 'none') == 'none' and
            f.get('ext') in self.VIDEO_FORMATS
        ]

        if video_formats:
            # Prefer mp4 for compatibility
            video_formats.sort(
                key=lambda x: (
                    x['ext'] != 'mp4',  # mp4 first
                    -x.get('height', 0),  # higher resolution first
                    -x.get('filesize', 0)  # larger file (better quality)
                )
            )
            self._stream_url = video_formats[0].get('url')

        # Find best audio-only stream
        audio_formats = [
            f for f in formats
            if f.get('acodec', 'none') != 'none' and
            f.get('vcodec', 'none') == 'none'
        ]

        if audio_formats:
            audio_formats.sort(
                key=lambda x: (
                    x['ext'] in ('m4a', 'aac'),  # prefer these
                    -x.get('abr', 0),  # higher bitrate first
                    -x.get('filesize', 0)
                )
            )
            self._audio_url = audio_formats[0].get('url')

        # Fallback: if no separate streams, use combined stream
        if not self._stream_url:
            combined_formats = [
                f for f in formats
                if f.get('vcodec', 'none') != 'none' and
                f.get('acodec', 'none') != 'none'
            ]

            if combined_formats:
                combined_formats.sort(
                    key=lambda x: (
                        x['ext'] == 'mp4',
                        -x.get('height', 0),
                        -x.get('abr', 0)
                    )
                )
                self._stream_url = combined_formats[0].get('url')
                self._audio_url = None  # Already combined

    def _build_ffmpeg_command(
        self,
        start_time: float,
        end_time: float,
        output_path: str,
        output_format: str
    ) -> list:
        """
        Build ffmpeg command for efficient clip extraction.

        Uses fast seeking (-ss before input) to avoid re-encoding.
        Downloads only the necessary portion of the video.

        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Output file path
            output_format: Output format (mp4 or mp3)

        Returns:
            List of ffmpeg command arguments
        """
        duration = end_time - start_time
        cmd = []

        # Input seeking (fast, no re-encoding)
        cmd.extend([self._get_ffmpeg_path(), '-ss', str(start_time)])

        # Input URL - use appropriate stream based on output format
        if output_format == 'mp3':
            # For audio-only output, use the audio stream
            stream_url = self._audio_url if self._audio_url else self._stream_url
        else:
            # For video output, use the video stream
            stream_url = self._stream_url

        if stream_url:
            cmd.extend(['-i', stream_url])
        else:
            # Fallback: fetch fresh URL
            cmd.extend(['-i', self.url])  # yt-dlp protocol

        # For MP4 with separate audio stream
        if output_format == 'mp4' and self._audio_url:
            # We need to use a more complex approach with multiple inputs
            # This will be handled in a separate method
            return self._build_ffmpeg_command_combined(
                start_time, end_time, output_path, output_format
            )

        # End time
        cmd.extend(['-t', str(duration)])

        # Codec options (fast, no re-encoding)
        if output_format == 'mp4':
            cmd.extend(['-c:v', 'copy', '-c:a', 'copy'])
        else:  # mp3
            cmd.extend(['-vn', '-acodec', 'libmp3lame', '-q:a', '2'])

        # Output format
        cmd.extend(['-f', output_format, output_path])

        return cmd

    def _build_ffmpeg_command_combined(
        self,
        start_time: float,
        end_time: float,
        output_path: str,
        output_format: str
    ) -> list:
        """
        Build ffmpeg command for combined video + audio streams.

        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Output file path
            output_format: Output format

        Returns:
            List of ffmpeg command arguments
        """
        duration = end_time - start_time
        cmd = [self._get_ffmpeg_path()]

        # Video input with seeking
        cmd.extend(['-ss', str(start_time), '-i', self._stream_url])

        # Audio input with seeking
        cmd.extend(['-ss', str(start_time), '-i', self._audio_url])

        # Duration
        cmd.extend(['-t', str(duration)])

        # Map streams
        cmd.extend(['-map', '0:v:0', '-map', '1:a:0'])

        # Copy codecs (no re-encoding)
        cmd.extend(['-c:v', 'copy', '-c:a', 'copy'])

        # Output
        cmd.extend(['-f', 'mp4', output_path])

        return cmd

    def _get_ffmpeg_path(self) -> str:
        """Get the ffmpeg executable path."""
        return FFMPEG_PATH if FFMPEG_PATH else 'ffmpeg'

    def create_clip(
        self,
        start_time: float,
        end_time: float,
        output_format: str = 'mp4',
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Optional[str]:
        """
        Create a clip from the YouTube video.

        This is the main method that orchestrates the clip creation process.

        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            output_format: Output format (mp4 or mp3)
            progress_callback: Optional callback for progress updates (0-1)

        Returns:
            Path to the created clip file or None on error

        Raises:
            ClipProcessingError: If clip creation fails
        """
        try:
            # Ensure we have video info
            if not self._video_info:
                self.get_video_info()

            if not self._stream_url:
                raise ClipProcessingError("Could not extract video stream URL")

            # Validate duration
            duration = end_time - start_time
            if duration > MAX_CLIP_DURATION:
                raise ClipProcessingError(
                    f"Clip duration exceeds maximum of {MAX_CLIP_DURATION} seconds"
                )

            # Generate output filename
            safe_title = "".join(
                c for c in self._video_info.title
                if c.isalnum() or c in (' ', '-', '_')
            ).rstrip()[:50]

            output_filename = f"{safe_title}_{start_time:.0f}-{end_time:.0f}.{output_format}"
            output_path = os.path.join(self.temp_dir, output_filename)

            # Build and execute ffmpeg command
            cmd = self._build_ffmpeg_command(
                start_time=start_time,
                end_time=end_time,
                output_path=output_path,
                output_format=output_format
            )

            if progress_callback:
                progress_callback(0.1)

            # Execute ffmpeg
            self._execute_ffmpeg(cmd, progress_callback)

            if progress_callback:
                progress_callback(1.0)

            # Verify output file exists
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Successfully created clip: {output_path}")
                return output_path
            else:
                raise ClipProcessingError("Output file was not created")

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e}")
            raise ClipProcessingError(f"FFmpeg processing failed: {str(e)}")
        except Exception as e:
            logger.error(f"Clip creation error: {e}")
            raise ClipProcessingError(f"Failed to create clip: {str(e)}")

    def _execute_ffmpeg(
        self,
        cmd: list,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> None:
        """
        Execute ffmpeg command and capture output.

        Args:
            cmd: FFmpeg command as list of arguments
            progress_callback: Optional progress callback

        Raises:
            subprocess.CalledProcessError: If ffmpeg fails
        """
        logger.debug(f"Executing FFmpeg: {' '.join(cmd)}")

        # For actual implementation, we'd parse ffmpeg output for progress
        # For now, just execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            error_output = result.stderr[-500:] if result.stderr else "Unknown error"
            logger.error(f"FFmpeg error output: {error_output}")
            raise subprocess.CalledProcessError(
                result.returncode,
                cmd,
                result.stdout,
                result.stderr
            )

        logger.info("FFmpeg completed successfully")

    def cleanup(self):
        """Clean up temporary resources."""
        self._video_info = None
        self._stream_url = None
        self._audio_url = None
