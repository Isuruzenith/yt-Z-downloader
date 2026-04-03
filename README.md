# yt-Z Downloader

**yt-Z Downloader** is a self-hosted, multi-user web application that wraps the powerful [yt-dlp](https://github.com/yt-dlp/yt-dlp) tool with a clean, responsive, browser-based UI. It eliminates the need for terminal access when downloading media from 1,000+ supported sites, running seamlessly inside a single Docker container.

---

## 🌟 Key Features

- **Zero-Terminal Experience:** A modern, mobile-friendly interface for enqueueing, monitoring, and downloading media.
- **Multi-User Isolation:** Each user has an isolated queue, isolated download history, and isolated cookie files to prevent overlap.
- **Real-Time WebSockets:** See live progress, ETA, and job statuses without refreshing the page.
- **Multi-Worker Execution:** Spin up concurrent background workers tailored to your host's capabilities.
- **Smart Presets:** Configure and save specific formats, qualities, embed metadata options, and custom arguments to re-use instantly.
- **YouTube Cookie Sync:** Includes a one-click Javascript Bookmarklet to pull cookies straight from your browser for age-restricted content.
- **Library Management:** View all downloaded media complete with extracted thumbnails, metadata JSON parsing, and powerful sorting tools.
- **Auto-Cleanup Task:** Automatically deletes stale files after a customizable number of days.
- **SponsorBlock Support:** Opt-in to automatically mark or remove sponsored segments.
- **Resilient Background Queue:** Powered by SQLite & asyncio. Queue withstands crashes and retries failed downloads with exponential backoff.

---

## 🚀 Quickstart Guide

yt-Z is explicitly built for frictionless self-hosting.

### 1. Clone the repository

```bash
git clone https://github.com/your-username/yt-Z-downloader.git
cd yt-Z-downloader
```

### 2. Configure Environment

Copy the example environment file and generate a secure secret key:

```bash
cp .env.example .env
```
*(Open `.env` and set `SECRET_KEY` to a random long string to secure your JWT sessions!)*

### 3. Deploy with Docker Compose

Run the provided `docker-compose.yml`:

```bash
docker compose up -d
```

The app is now running on your server on **Port 8000**! Navigate to `http://localhost:8000` to create your first account and log in. 

---

## ⚙️ Configuration Reference

All settings are customized via the `.env` file mounted by Docker Compose. You do not need to rebuild the container to change these options.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(required)* | 32+ character random string used for signing authentication JWT tokens. |
| `PORT` | `8000` | The port the FastAPI server binds to. |
| `DOWNLOAD_ROOT` | `/downloads` | Internal container path where media files are saved. Mapped to your host. |
| `COOKIES_ROOT` | `/cookies` | Internal path where isolated `cookies.txt` files reside. |
| `DATA_ROOT` | `/data` | Internal path where the `yt_z.db` SQLite database is maintained. |
| `MAX_QUEUE_SIZE` | `50` | Maximum number of unstarted jobs an individual user can have. |
| `MAX_RETRIES` | `3` | yt-dlp internal auto-retry attempts upon a download fragment failure. |
| `WORKER_COUNT` | `1` | Number of concurrent async download workers to spawn. |
| `MAX_DOWNLOAD_AGE_DAYS` | `0` | If `> 0`, automatically deletes media files older than this many days via a 12h cron task. |
| `JS_RUNTIME` | `deno` | JS execution backend (`deno` or `node`) for extracting YouTube signatures. Deno is included in our container. |
| `ENABLE_SPONSORBLOCK`| `False` | Set to `True` to allow users to opt-in to SponsorBlock (mark/remove) via the Advanced Options menu. |
| `ENABLE_POWER_MODE` | `False` | Set to `True` to enable raw `yt-dlp` arguments passthrough (filtered by strict allowlist). |

---

## 🍪 Bookmarklet Setup

For sites like YouTube that demand active cookies for high-quality or age-restricted formats, downloading `cookies.txt` manually can be tedious. We built a bookmarklet to fix this!

1. Open your yt-Z Downloader **Settings** page.
2. Find the **"🔖 yt-Z Cookie Sync"** button.
3. **Click and Drag** that button directly into your browser's Bookmarks/Favorites Bar.
4. Navigate to `https://www.youtube.com/` and ensure you are logged into your account.
5. Click the newly created bookmarklet in your bar. A prompt will confirm that your cookies have successfully synced back to your yt-Z server!

*Note: For HttpOnly cookies or complex sessions, you can still manually upload a `cookies.txt` via the Settings menu.*

---

## 📖 API Documentation

yt-Z Downloader leverages FastAPI to expose a meticulously documented REST architecture under the hood. 

Once your container is running, navigate to:

> **[http://localhost:8000/docs](http://localhost:8000/docs)**

This opens an interactive **Swagger UI** where you can:
1. Examine schemas and endpoints (`GET /api/queue`, `POST /api/download`, `GET /api/library`, etc.).
2. Authenticate directly inside Swagger using the `Authorize` button.
3. Test programmatic API calls and observe payload responses directly from your browser.

---

### Built With:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLite](https://www.sqlite.org/index.html) (SQLAlchemy/Aiosqlite)
- [FFmpeg](https://ffmpeg.org/)
- HTML/CSS Vanilla JavaScript (Zero-Build Frontend)

*Designed for seamless home server operation and media archival.*
