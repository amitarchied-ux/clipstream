"""
YouTube Video Clipper - Vercel Serverless API

FastAPI-based backend optimized for Vercel serverless functions.
This provides an alternative architecture for Vercel deployment.

Architecture:
- Next.js frontend (separate)
- FastAPI backend (this file)
- Serverless functions for each operation
"""
import os
import tempfile
import logging
from typing import Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, validator, Field
from mangum import Mangum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Temp directory for Vercel serverless
TEMP_DIR = "/tmp/clipstream"
os.makedirs(TEMP_DIR, exist_ok=True)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ClipRequest(BaseModel):
    """Request model for clip creation."""
    url: str = Field(..., description="YouTube video URL")
    start_time: str = Field(..., description="Start time (MM:SS or HH:MM:SS)")
    end_time: str = Field(..., description="End time (MM:SS or HH:MM:SS)")
    format: str = Field(default="mp4", description="Output format (mp4 or mp3)")

    @validator('format')
    def validate_format(cls, v):
        if v not in ['mp4', 'mp3']:
            raise ValueError('Format must be mp4 or mp3')
        return v

    @validator('url')
    def validate_url(cls, v):
        if not v or ('youtube.com' not in v and 'youtu.be' not in v):
            raise ValueError('Invalid YouTube URL')
        return v


class VideoInfo(BaseModel):
    """Video information model."""
    title: str
    duration: int
    channel: str
    thumbnail: str
    duration_formatted: str


class ClipResponse(BaseModel):
    """Response model for clip creation."""
    success: bool
    download_url: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="ClipStream API",
    description="YouTube video clipping API optimized for Vercel",
    version="1.0.0"
)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def parse_timestamp(timestamp: str) -> float:
    """Parse timestamp string to seconds."""
    import re
    timestamp = timestamp.strip()

    hms_match = re.match(r'^(\d+):(\d{2}):(\d{2})$', timestamp)
    if hms_match:
        h, m, s = hms_match.groups()
        return int(h) * 3600 + int(m) * 60 + int(s)

    ms_match = re.match(r'^(\d+):(\d{2})$', timestamp)
    if ms_match:
        m, s = ms_match.groups()
        return int(m) * 60 + int(s)

    raise ValueError(f"Invalid timestamp: {timestamp}")


def format_timestamp(seconds: float) -> str:
    """Format seconds to timestamp string."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)

    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def sanitize_filename(name: str) -> str:
    """Sanitize filename for safe usage."""
    import re
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:50] if name else "clip"


def cleanup_old_files():
    """Clean up old temp files."""
    try:
        cutoff = datetime.now() - timedelta(hours=1)
        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(filepath):
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime < cutoff:
                    os.remove(filepath)
                    logger.info(f"Cleaned up: {filename}")
    except Exception as e:
        logger.warning(f"Cleanup error: {e}")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "ClipStream API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "video_info": "/api/video-info",
            "create_clip": "/api/create-clip",
            "download_clip": "/api/download/{clip_id}"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/video-info", response_model=VideoInfo)
async def get_video_info(url: str):
    """
    Get video information without downloading.

    Note: For Vercel deployment, this is a simplified version.
    In production, you'd use yt-dlp to fetch actual video info.
    """
    # Placeholder - implement with yt-dlp for production
    return VideoInfo(
        title="Video Title (implement with yt-dlp)",
        duration=300,
        channel="Channel Name",
        thumbnail="",
        duration_formatted="05:00"
    )


@app.post("/api/create-clip", response_model=ClipResponse)
async def create_clip(request: ClipRequest, background_tasks: BackgroundTasks):
    """
    Create a clip from YouTube video.

    Note: For Vercel deployment with 60s timeout:
    - Use external worker service for long-running tasks
    - Return a job ID immediately
    - Poll for status

    This is a simplified implementation.
    """
    try:
        # Parse timestamps
        start_sec = parse_timestamp(request.start_time)
        end_sec = parse_timestamp(request.end_time)

        if end_sec <= start_sec:
            raise HTTPException(400, "End time must be after start time")

        duration = end_sec - start_sec
        if duration > 600:  # 10 minutes max for serverless
            raise HTTPException(400, "Clip too long for serverless processing")

        # For Vercel serverless, we'd typically:
        # 1. Queue the job (Redis/SQS)
        # 2. Return job ID
        # 3. Have worker process on separate infrastructure
        # 4. Provide status/download endpoint

        # Simplified response for demonstration
        return ClipResponse(
            success=False,
            error="Serverless deployment requires external worker service. See README."
        )

    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Clip creation error: {e}")
        raise HTTPException(500, "Internal server error")


@app.get("/api/download/{clip_id}")
async def download_clip(clip_id: str):
    """
    Download a processed clip.

    For Vercel: Files should be stored in object storage (R2/S3),
    not in the serverless filesystem.
    """
    # Placeholder - implement with object storage
    raise HTTPException(404, "Clip not found or expired")


# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# ============================================================================
# VERCEL WRAPPER
# ============================================================================

# AWS Lambda handler for Vercel
handler = Mangum(app, lifespan="off")


# ============================================================================
# STARTUP EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run cleanup on startup."""
    cleanup_old_files()


# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
