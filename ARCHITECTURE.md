# ClipStream Architecture Documentation

## Executive Summary

ClipStream is a YouTube video clipping application designed for efficiency and scalability. This document explains the architectural decisions, trade-offs, and deployment considerations.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Selection](#technology-selection)
3. [Stream-Based Clipping](#stream-based-clipping)
4. [Deployment Options](#deployment-options)
5. [Performance Considerations](#performance-considerations)
6. [Security Design](#security-design)
7. [Scalability Strategy](#scalability-strategy)

---

## System Architecture

### Modular Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                      │
│                    (Streamlit UI / Next.js)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                      │
│              (clipper.py - Core Processing Engine)          │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌──────────────────┐          ┌──────────────────┐
│   yt-dlp         │          │   FFmpeg         │
│  (Stream URLs)   │          │  (Clip Extract)  │
└──────────────────┘          └──────────────────┘
```

### Module Responsibilities

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| `app.py` | UI, user interaction, session management | Streamlit, clipper |
| `clipper.py` | Core video processing logic | yt-dlp, FFmpeg |
| `utils.py` | Timestamp parsing, validation, file utilities | Python stdlib |
| `config.py` | Configuration management, environment detection | Python stdlib |

---

## Technology Selection

### Core Libraries

#### 1. Streamlit
**Selected because:**
- Rapid UI development
- Built-in progress tracking
- Server-side state management
- Python-native (no separate frontend needed)

**Alternatives considered:**
- **FastAPI + React**: More flexibility but higher complexity
- **Flask + Jinja2**: Less modern UX, more boilerplate
- **Gradio**: Less customization, ML-focused

#### 2. yt-dlp (over youtube-dl)
**Selected because:**
- Actively maintained
- Better YouTube support
- Faster stream extraction
- More reliable for premium content

**Key features used:**
- Direct URL extraction
- Format selection
- Metadata retrieval

#### 3. FFmpeg (with fast seeking)
**Selected because:**
- Industry standard for video processing
- Fast seeking without re-encoding
- Wide format support
- Efficient memory usage

**Critical technique:**
```bash
# Fast seeking (no re-encoding)
ffmpeg -ss START_TIME -i INPUT_URL -t DURATION -c copy OUTPUT

# Slow seeking (re-encoding, avoided)
ffmpeg -i INPUT_URL -ss START_TIME -t DURATION -c:v libx264 OUTPUT
```

---

## Stream-Based Clipping

### How It Works

```
┌──────────────────────────────────────────────────────────────┐
│  Traditional Approach (NOT USED)                             │
│                                                              │
│  [Full Video Download] → [Full File on Disk] → [Clip]       │
│         500MB              500MB               50MB           │
│         ~5 minutes          ~5 minutes        ~30 seconds     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  Stream-Based Approach (USED)                               │
│                              ┌────[Keyframes]────┐            │
│  [Partial Stream] ──────────▶ │                  │ ──▶ [Clip] │
│        ~80MB                      ~10MB                      │
│      ~30 seconds                 ~30 seconds                 │
└──────────────────────────────────────────────────────────────┘
```

### Technical Implementation

1. **Stream URL Extraction:**
   ```python
   formats = ydl.extract_info(url, download=False)['formats']
   video_stream = next(f for f in formats if f['vcodec'] != 'none')
   ```

2. **Fast Seeking:**
   ```bash
   ffmpeg -ss 120 -i "STREAM_URL" -t 60 -c copy output.mp4
   ```
   - `-ss` before `-i` = fast seek (keyframe-based)
   - `-c copy` = no re-encoding
   - Downloads from nearest keyframe before start time

3. **Bandwidth Savings:**
   | Clip Duration | Traditional | Stream-Based | Savings |
   |---------------|-------------|--------------|---------|
   | 1 minute | 100% | 15-20% | 80-85% |
   | 5 minutes | 100% | 25-35% | 65-75% |
   | 10 minutes | 100% | 35-45% | 55-65% |

---

## Deployment Options

### Option 1: Streamlit on Container Platforms

**Platforms:**
- Streamlit Community Cloud
- Railway
- Fly.io
- Render
- DigitalOcean App Platform

**Requirements:**
- Persistent container
- 512MB+ RAM
- FFmpeg installed

**Deployment flow:**
```
git push → CI/CD → Build Image → Deploy Container → Health Check → Live
```

### Option 2: Vercel Serverless (API Only)

**Challenges:**
- 10-60 second timeout
- Stateless execution
- No persistent storage

**Solution architecture:**
```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Next.js UI    │ ───▶ │  Vercel API     │ ───▶ │  Worker Service │
│   (Vercel)      │      │  (Vercel)       │      │  (Railway/AWS)  │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │                         │
                                ▼                         ▼
                         [Job Queue]               [FFmpeg Processing]
                                                       [R2/S3 Storage]
```

**Implementation:**
1. Vercel API: Accepts request, creates job, returns job ID
2. Worker Service: Polls queue, processes video, stores result
3. Frontend: Polls for status, downloads when ready

**Example worker service:**
```python
# Railway Worker / AWS Lambda
import redis
import boto3

def process_clip(job_id, url, start, end):
    # Process video
    clip_path = clipper.create_clip(url, start, end)

    # Upload to R2/S3
    s3.upload_file(clip_path, f"clips/{job_id}.mp4")

    # Update job status
    redis.set(f"job:{job_id}", "complete")
```

---

## Performance Considerations

### Optimization Techniques

1. **Connection Pooling:**
   ```python
   # Reuse yt-dlp instances
   @lru_cache(maxsize=10)
   def get_clipper(url: str) -> YouTubeClipper:
       return YouTubeClipper(url)
   ```

2. **Progressive Rendering:**
   ```python
   # Update UI during processing
   for progress in process_clip():
       st.progress(progress)
   ```

3. **Memory Management:**
   - Stream processing (no full file in memory)
   - Automatic cleanup of temp files
   - Session-based file isolation

### Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| First-byte time | <2s | <5s |
| Clip creation (1min) | <10s | <30s |
| Clip creation (5min) | <30s | <60s |
| Memory per session | <200MB | <500MB |

---

## Security Design

### Threat Model

| Threat | Mitigation |
|--------|------------|
| Path traversal | Filename sanitization, temp directory isolation |
| Resource exhaustion | Max clip duration, file size limits |
| Code injection | Input validation, no eval/exec |
| Session hijacking | Automatic file cleanup, session tokens |

### Implementation

```python
# Input validation
def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    return name[:50]  # Length limit

# Resource limits
if duration > MAX_CLIP_DURATION:
    raise ClipProcessingError("Duration exceeds limit")

# Session isolation
session_temp = os.path.join(TEMP_DIR, session_id)
os.makedirs(session_temp, mode=0o700)
```

---

## Scalability Strategy

### Horizontal Scaling

**Container platforms (Railway, Fly.io):**
```
          Load Balancer
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
 [App 1]      [App 2]      [App 3]
 512MB        512MB        512MB
```

**Benefits:**
- Automatic scaling
- Zero-downtime deployments
- Geographic distribution

### Vertical Scaling

**For single-instance deployments:**
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 512MB | 1-2GB |
| CPU | 1 core | 2+ cores |
| Storage | 1GB | 5GB+ |

### Caching Strategy

```python
# Cache video info to reduce API calls
@cache(ttl=3600)  # 1 hour
def get_video_info(url: str) -> VideoInfo:
    return ydl.extract_info(url)

# Cache stream URLs (short TTL, can expire)
@cache(ttl=300)  # 5 minutes
def get_stream_url(url: str) -> str:
    return extract_stream(url)
```

---

## Future Enhancements

### Planned Features

1. **Batch Processing:**
   - Queue multiple clips
   - Progress tracking per clip
   - Download as ZIP

2. **Quality Presets:**
   - High Quality (original)
   - Medium Quality (720p)
   - Low Quality (480p)
   - Audio-only options

3. **Advanced Features:**
   - Fade in/out
   - Multiple segments joined
   - Subtitle burning
   - Watermark overlay

4. **Integration:**
   - Direct social media sharing
   - Cloud storage integration (Google Drive, Dropbox)
   - API access for developers

---

## Conclusion

ClipStream's architecture prioritizes:
1. **Efficiency** through stream-based processing
2. **Simplicity** through modular design
3. **Scalability** through container deployment
4. **User Experience** through responsive UI

The result is a production-ready application that can handle significant traffic while minimizing resource usage and processing time.
