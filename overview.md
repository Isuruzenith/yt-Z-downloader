# yt-Z-Downloader — Project Overview

---

## 1. What Is This?

**yt-Z-Downloader** is a self-hosted web application that wraps **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — the leading open-source downloader supporting 1000+ sites — with a clean browser UI.

> Paste a URL → pick format & quality → download. No terminal needed. Runs entirely on your server via Docker.

Handles age-restricted, premium/preview, member-only, and geo-blocked content via per-user cookie management.

---

## 2. Why Build This?

yt-dlp is the best extractor available, but it has friction:

| Problem | This Project Solves It With |
|---|---|
| CLI-only → hard for non-tech users | Clean, mobile-friendly web UI |
| Manual cookie export (expires often) | One-click YouTube bookmarklet sync |
| No queue or history across devices | Persistent async queue + SQLite history |
| Bot detection / JS signature changes | yt-dlp nightly + Deno/Node JS runtime |
| Multi-device setup complexity | Docker: `docker compose up` → ready in < 2 min |

---

## 3. Architecture

```
Browser (HTML/JS)
       ↕  REST API (polling every 2–3s)
FastAPI (Uvicorn, async)
       ↕
Async Queue (asyncio.Queue + thread pool executor)
       ↕
yt-dlp (+ ffmpeg)
       ↕
SQLite ── users • jobs • history
       ↕
/downloads  (per-user folders)
/cookies    (per-user cookie files)
```

**Key design decisions:**
- **Single sequential worker** — prevents bandwidth/CPU overload; configurable for multi-worker later
- **yt-dlp runs in executor** — keeps FastAPI event loop unblocked
- **Polling-based progress** — simple, reliable; WebSocket upgrade path planned
- **Per-user isolation** — files, cookies, queue, and history are scoped to each user ID

---

## 4. Key Features

### 4.1 Download Capabilities
- 1000+ sites via yt-dlp (nightly channel recommended)
- **Formats:** MP4 (merged), MKV, WEBM, MP3, M4A, Best
- **Quality presets:** 4K / 1440p / 1080p / 720p / 480p / Audio-only / Best
- Playlist support (toggle per download)
- Metadata preview before download: title, uploader, duration, thumbnail, available formats
- Auto-retry (3× default) + sleep intervals to handle throttling

### 4.2 Cookie & Authentication System
- **Per-user cookies** — upload Netscape/JSON cookie file or use one-click YouTube sync
- **YouTube Bookmarklet ("yt-Z Cookie Sync")**
  1. Drag bookmarklet to browser bookmarks bar (one-time setup)
  2. Navigate to `youtube.com` while logged in → click bookmarklet
  3. Cookies auto-extracted → POSTed to your server → "Sync Complete!"
  4. No manual export ever again — most reliable method in 2026
- Fallback: global cookies file on the server
- Optional: `--cookies-from-browser firefox` if browser is on the same host

### 4.3 Queue & Progress
- Unlimited queue (soft limit: 50, configurable via `.env`)
- Real-time % progress + estimated download size
- Cancel queued jobs before execution
- Sequential execution — avoids YouTube rate-limit spikes

### 4.4 User & Security
- Register / Login (email + PBKDF2-HMAC-SHA256 password hashing)
- JWT authentication (HS256, 24h expiry)
- Complete per-user data isolation
- History with pagination (SQLite-backed)

### 4.5 Frontend
- Vanilla HTML + CSS + JS — no framework, no build step
- Dark theme + responsive / mobile-friendly design
- Auto-paste URL from clipboard on focus
- Nav badge shows active queue count

### 4.6 Deployment & Ops
- **Docker-first** — single container: Python 3.11-slim + ffmpeg + yt-dlp nightly
- Named volumes: `/downloads`, `/cookies`, `/data` (SQLite)
- Health check endpoint: `GET /health`
- All config via `.env` file (no code changes needed)

---

## 5. Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Backend | FastAPI + Uvicorn | Async, OpenAPI docs at `/docs`, Pydantic validation |
| Downloader | yt-dlp (nightly) + ffmpeg | Best extractor; ffmpeg required for format merging & audio |
| JS Runtime | Deno (recommended) or Node.js | Required for YouTube signature extraction in 2026 |
| Database | SQLite + SQLAlchemy + aiosqlite | Zero-config, async, perfect for self-hosted single instance |
| Auth | python-jose (JWT) + PBKDF2 | Stateless tokens, secure password hashing |
| Frontend | Vanilla HTML / CSS / JS | Lightweight, no npm, instant deploy |
| Containerization | Docker + Compose | Single command startup, portable across hosts |
| Testing / CI | pytest + ruff + GitHub Actions | Lint, test, auto-build & push Docker images |

---

## 6. Project Structure

```
yt-z-downloader/
├── api/
│   ├── main.py           # FastAPI app entry, router registration, CORS
│   ├── downloader.py     # yt-dlp Python API wrapper + progress hooks
│   ├── queue.py          # asyncio.Queue + single background worker
│   ├── auth.py           # JWT creation / validation, login logic
│   ├── users.py          # User registration, profile endpoints
│   ├── history.py        # Download history CRUD
│   ├── models.py         # Pydantic request/response schemas
│   ├── db.py             # SQLAlchemy async engine + ORM table definitions
│   └── config.py         # Settings loaded from .env via Pydantic BaseSettings
├── frontend/
│   ├── index.html        # Main download page
│   ├── queue.html        # Active queue view
│   ├── history.html      # Download history view
│   ├── settings.html     # Cookie upload + user settings
│   ├── login.html        # Login / Register
│   ├── app.js            # Shared JS (API calls, auth, UI helpers)
│   └── style.css         # Dark theme, responsive layout
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_queue.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                 # GitHub Pages landing page
├── .github/workflows/    # CI: lint, test, build & push image
├── requirements.txt
├── .env.example
└── README.md
```

---

## 7. Configuration (`.env`)

```env
SECRET_KEY=super-secret-change-me       # JWT signing key — MUST change
DOWNLOAD_ROOT=/downloads                 # Host volume for downloaded files
COOKIES_ROOT=/cookies                    # Host volume for cookie files
DATA_ROOT=/data                          # Host volume for SQLite database
MAX_QUEUE_SIZE=50                        # Max queued jobs per instance
MAX_RETRIES=3                            # yt-dlp auto-retry attempts
DEFAULT_FORMAT=mp4                       # Default output format
YTDLP_CHANNEL=nightly                   # "nightly" or "stable"
JS_RUNTIME=deno                          # "deno" or "node" (for YT sig extraction)
PORT=8000
```

---

## 8. API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create new user account |
| `POST` | `/auth/login` | Authenticate, receive JWT |
| `GET` | `/api/info?url=...` | Fetch video metadata + available formats |
| `POST` | `/api/download` | Enqueue a new download job |
| `GET` | `/api/queue` | List active jobs + live progress |
| `DELETE` | `/api/queue/{job_id}` | Cancel a queued job |
| `GET` | `/api/downloads` | Paginated download history |
| `POST` | `/api/settings/cookies/youtube` | Bookmarklet cookie sync endpoint |
| `GET` | `/health` | Container health check |
| `GET` | `/docs` | Swagger UI (auto-generated) |

---

## 9. Roadmap

- [ ] Optional multi-worker mode (concurrent downloads)
- [ ] WebSocket progress (replace polling)
- [ ] Format presets & custom yt-dlp args per user
- [ ] Thumbnail embedding + basic media server
- [ ] `--impersonate chrome` / PO token auto-fetch toggle
- [ ] Admin panel for global settings

---

**License:** MIT
