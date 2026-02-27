# ClipStream | Premium YouTube Video Clipper

A production-ready, efficient YouTube video clipping application that extracts clips without downloading the full video file.

## 🎯 Features

- **Stream-Based Processing**: Uses FFmpeg fast seeking - only downloads necessary video segments
- **Multiple Formats**: Export as MP4 (video) or MP3 (audio only)
- **Flexible Timestamps**: Support for MM:SS and HH:MM:SS formats
- **Auto Cleanup**: Temporary files are automatically deleted after processing
- **Premium UI**: Modern, polished interface (emerald/gold color scheme)
- **Production Ready**: Modular architecture, proper error handling, logging

## 🏗️ Architecture

### Why Two Deployment Options?

**Streamlit is NOT natively compatible with Vercel** because:
- Streamlit requires a persistent Python process with WebSocket connections
- Vercel serverless functions have 10-60 second execution timeouts
- Video processing typically exceeds these limits

I've provided two complete solutions:

### Option 1: Streamlit Application (`streamlit_app/`)

**Best for:**
- Streamlit Community Cloud (free tier available)
- Railway, Fly.io, Render, DigitalOcean App Platform
- Any container-based platform

**Architecture:**
```
streamlit_app/
├── app.py           # Main UI application
├── clipper.py       # Core video processing engine
├── utils.py         # Utility functions
├── config.py        # Configuration management
├── Dockerfile       # Container image
└── requirements.txt # Python dependencies
```

### Option 2: Vercel Serverless API (`vercel_api/`)

**Best for:**
- Vercel deployment with Next.js frontend (you provide)
- External worker service for long-running tasks

**Architecture:**
```
vercel_api/
├── api/
│   └── index.py     # FastAPI endpoints
├── vercel.json      # Vercel configuration
└── requirements.txt # Python dependencies
```

**Note:** For production Vercel deployment, you need:
1. This API layer
2. A Next.js frontend
3. An external worker service (Railway Worker, AWS Lambda, etc.) for video processing

## 🚀 Quick Start

### Streamlit Version (Recommended)

#### Local Development

1. **Install FFmpeg:**
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg

   # Windows (using Chocolatey)
   choco install ffmpeg
   ```

2. **Install Python Dependencies:**
   ```bash
   cd streamlit_app
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

4. **Open in Browser:**
   ```
   http://localhost:8501
   ```

#### Deploy to Streamlit Community Cloud

1. **Push your code to GitHub**
2. **Go to [streamlit.io/cloud](https://streamlit.io/cloud)**
3. **Click "New app" and connect your repository**
4. **Set main file path to `streamlit_app/app.py`**
5. **Deploy!**

#### Deploy to Railway/Fly.io/Render

**Railway:**
```bash
# Install Railway CLI
npm install -g railway

# Login and deploy
railway login
railway init
railway up
```

**Fly.io:**
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

**Render:**
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your repository
5. Set build command: `pip install -r streamlit_app/requirements.txt`
6. Set start command: `streamlit run streamlit_app/app.py --server.port=$PORT`
7. Deploy!

### Vercel Serverless Version

**Prerequisites:** External worker service required for video processing

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy API:**
   ```bash
   cd vercel_api
   vercel
   ```

3. **Create Next.js frontend** (you provide) that calls the API endpoints

## 📋 Environment Variables

### Streamlit Version

| Variable | Description | Default |
|----------|-------------|---------|
| `CLIPSTREAM_TEMP_DIR` | Temporary files directory | System temp |
| `FFMPEG_PATH` | FFmpeg executable path | `ffmpeg` (from PATH) |
| `CLIPSTREAM_MAX_DURATION` | Max clip duration (seconds) | `1800` (30 min) |
| `CLIPSTREAM_SESSION_TIMEOUT` | Session cleanup timeout | `30` (minutes) |
| `CLIPSTREAM_LOG_LEVEL` | Logging level | `INFO` |

### Vercel Version

Set in `vercel.json` or Vercel dashboard:
- `CLIPSTREAM_ENV`: Set to `production`

## 🎨 Customization

### Change Color Scheme

Edit `config.py` in `streamlit_app/`:

```python
UI_CONFIG = {
    'colors': {
        'primary': '#10b981',      # Your color
        'secondary': '#f59e0b',    # Your color
        # ... etc
    }
}
```

### Adjust Clip Limits

```python
MAX_CLIP_DURATION = 3600  # 1 hour max
```

### Add New Output Formats

Edit `clipper.py` and add to `QUALITY_PRESETS`.

## 🔧 Technical Details

### How Stream-Based Clipping Works

1. **yt-dlp** extracts direct stream URLs from YouTube
2. **FFmpeg** uses fast seeking (`-ss` before input) to jump to start position
3. Only the video segment + nearby keyframes are downloaded
4. No re-encoding = maximum speed and quality preservation

### Performance Characteristics

| Video Length | Download Time | Processing Time |
|--------------|---------------|-----------------|
| 1 minute clip | ~5-15 seconds | ~2-5 seconds |
| 5 minute clip | ~15-45 seconds | ~5-15 seconds |
| 10 minute clip | ~30-90 seconds | ~10-30 seconds |

*Actual times vary based on connection speed and video quality*

## 🛡️ Security Considerations

- Input validation on all user inputs
- Temporary files are automatically cleaned up
- No arbitrary code execution
- No file path traversal vulnerabilities
- Session-based file isolation

## 📊 Monitoring (Optional)

For production deployment, consider adding:

```python
# In requirements.txt
sentry-sdk[streamlit]>=1.38.0

# In app.py
import sentry_sdk
sentry_sdk.init(dsn="YOUR_SENTRY_DSN")
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx-mock

# Run tests
pytest
```

## 📄 License

MIT License - feel free to use in your projects!

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation

---

Built with ❤️ using Streamlit, yt-dlp, and FFmpeg
