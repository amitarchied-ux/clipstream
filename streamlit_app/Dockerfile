# YouTube Video Clipper - Production Docker Image
# Optimized for container-based deployment (Railway, Fly.io, Render, etc.)

# ============================================================================
# BASE IMAGE
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# ============================================================================
# FFMPEG INSTALLATION
# ============================================================================
# Install FFmpeg and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# DEPENDENCIES
# ============================================================================
# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ============================================================================
# APPLICATION CODE
# ============================================================================
# Copy application code
COPY . .

# ============================================================================
# USER & PERMISSIONS
# ============================================================================
# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Create temp directory with proper permissions
RUN mkdir -p /tmp/clipstream && \
    chmod 755 /tmp/clipstream

# Set temp directory environment variable
ENV CLIPSTREAM_TEMP_DIR=/tmp/clipstream

# ============================================================================
# EXPOSE & HEALTH CHECK
# ============================================================================
# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8501/_stcore/health || exit 1

# ============================================================================
# START COMMAND
# ============================================================================
# Start Streamlit with production settings
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true", \
     "--browser.gatherUsageStats=false", \
     "--logger.level=info"]
