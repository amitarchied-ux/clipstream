# ClipStream Quick Start Guide

Get ClipStream running in under 5 minutes.

## Prerequisites

- Python 3.9 or higher
- FFmpeg installed
- Git (optional, for cloning)

---

## Method 1: Local Development (Fastest)

### 1. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows (Chocolatey):**
```bash
choco install ffmpeg
```

### 2. Clone or Download

```bash
# If you have the project
cd S:/video-cliper/streamlit_app

# Or clone from git
git clone <repository-url>
cd video-cliper/streamlit_app
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
streamlit run app.py
```

### 5. Open Browser

Navigate to `http://localhost:8501`

---

## Method 2: Docker (Recommended for Consistency)

### 1. Install Docker

[Download Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2. Run with Docker Compose

```bash
cd S:/video-cliper
docker-compose up
```

### 3. Open Browser

Navigate to `http://localhost:8501`

---

## Method 3: Streamlit Community Cloud (Free Hosting)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Deploy to Streamlit Cloud

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click "New app"
3. Connect your GitHub repository
4. Set:
   - **Main file path**: `streamlit_app/app.py`
   - **Python version**: `3.11`
5. Click "Deploy"

### 3. Wait for Deployment

Usually takes 2-3 minutes. Your app will be live at `https://your-app-name.streamlit.app`

---

## Method 4: Railway (Simplest Container Deploy)

### 1. Install Railway CLI

```bash
npm install -g railway
```

### 2. Login and Deploy

```bash
cd S:/video-cliper/streamlit_app
railway login
railway init
railway up
```

### 3. Get Your URL

Railway will provide a live URL (e.g., `https://your-app.up.railway.app`)

---

## Method 5: Fly.io (Global Edge Deployment)

### 1. Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Deploy

```bash
cd S:/video-cliper/streamlit_app
fly launch
fly deploy
```

### 3. Access Your App

```bash
fly open
```

---

## Environment Variables (Optional)

For production, consider setting:

```bash
# Maximum clip duration (seconds)
export CLIPSTREAM_MAX_DURATION=1800

# Session timeout (minutes)
export CLIPSTREAM_SESSION_TIMEOUT=30

# Log level
export CLIPSTREAM_LOG_LEVEL=INFO
```

---

## Quick Test

Once running:

1. **Paste a YouTube URL:**
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

2. **Set timestamps:**
   - Start: `00:00`
   - End: `00:30`

3. **Select format:**
   - MP4 (Video) or MP3 (Audio)

4. **Click "Generate Clip"**

5. **Wait for processing** (usually 10-30 seconds)

6. **Download your clip!**

---

## Troubleshooting

### FFmpeg not found

**Symptom:** `FFmpeg not found at ffmpeg`

**Solution:**
- Install FFmpeg (see step 1 of Method 1)
- Or set `FFMPEG_PATH` to your FFmpeg location

### Port already in use

**Symptom:** `Address already in use`

**Solution:**
```bash
# Kill existing process
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run app.py --server.port 8502
```

### Module not found

**Symptom:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
# Make sure you're in streamlit_app directory
cd streamlit_app
pip install -r requirements.txt
```

### Video processing fails

**Symptom:** `Processing error` or `FFmpeg processing failed`

**Possible causes:**
- Video is private/restricted
- Video too long (max 30 minutes by default)
- Network issues

**Solution:**
- Try a different video
- Check video is publicly accessible
- Increase `MAX_CLIP_DURATION` in config.py

---

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Read [README.md](README.md) for full documentation
- Customize colors in `config.py`
- Adjust limits in `config.py`

---

## Need Help?

- Open an issue on GitHub
- Check FFmpeg is properly installed: `ffmpeg -version`
- Check Python version: `python --version` (should be 3.9+)

Happy clipping! 🎬
