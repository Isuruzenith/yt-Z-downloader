# yt-Z Downloader

A self-hosted web UI for [yt-dlp](https://github.com/yt-dlp/yt-dlp). Paste a URL, pick a format, download — no terminal required. Runs entirely in Docker.

![Python](https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)

---

## Features

- **1000+ sites** — every source yt-dlp supports
- **Format & quality presets** — MP4 / MKV / WEBM / MP3 / M4A, 4K → 480p → audio-only
- **Async queue** — jobs run sequentially in the background; live %-progress polling
- **Save to PC** — one-click browser download of the finished file
- **Cookie management** — upload a Netscape `cookies.txt` or use the YouTube bookmarklet to sync cookies from your browser with one click
- **Multi-user** — JWT auth, every user's files and cookies are fully isolated
- **Download history** — paginated SQLite-backed history with re-download links
- **Docker-first** — single container, named volumes, health check, < 2 min to running

---

## Quick Start

**1. Clone and configure**

```bash
git clone https://github.com/Isuruzenith/yt-Z-downloader.git
cd yt-Z-downloader

cp .env.example .env
```

Open `.env` and set a real secret key:

```bash
# Generate one:
openssl rand -hex 32
```

**2. Start**

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

**3. Open**

```
http://localhost:8000
```

Register an account → paste a URL → download.
Swagger API docs: `http://localhost:8000/docs`

---

## Configuration

All options are set via `.env` (no code changes needed):

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(required)* | JWT signing key — change before first run |
| `DOWNLOAD_ROOT` | `/downloads` | Volume path for downloaded files |
| `COOKIES_ROOT` | `/cookies` | Volume path for per-user cookie files |
| `DATA_ROOT` | `/data` | Volume path for SQLite database |
| `MAX_QUEUE_SIZE` | `50` | Maximum queued jobs |
| `MAX_RETRIES` | `3` | yt-dlp auto-retry attempts per job |
| `DEFAULT_FORMAT` | `mp4` | Default output format |
| `JS_RUNTIME` | `deno` | `deno` or `node` — required for YouTube sig extraction |
| `PORT` | `8000` | Listening port |

---

## Cookie Setup

Cookies are required for age-restricted, members-only, and some geo-blocked content.

### Option A — YouTube Bookmarklet (recommended)

1. Go to **Settings → Cookie Sync** in the app
2. Drag **"yt-Z Cookie Sync"** to your browser's bookmarks bar
3. Navigate to `youtube.com` while logged in
4. Click the bookmarklet → cookies sync automatically

> The bookmarklet only captures cookies accessible via JavaScript. HttpOnly cookies (used for full auth) require the file upload method below.

### Option B — File Upload

Export `cookies.txt` in Netscape format using a browser extension such as [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc), then upload it on the **Settings** page.

---

## API Reference

All endpoints except `/auth/*` and `/health` require `Authorization: Bearer <token>`.

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create account → returns JWT |
| `POST` | `/auth/login` | Authenticate → returns JWT |
| `GET` | `/api/info?url=` | Fetch video metadata and available formats |
| `POST` | `/api/download` | Enqueue a download job |
| `GET` | `/api/queue` | List your jobs with live progress |
| `DELETE` | `/api/queue/{id}` | Cancel a queued job |
| `GET` | `/api/queue/{id}/file` | Download the finished file to browser |
| `GET` | `/api/downloads` | Paginated history (terminal-state jobs) |
| `POST` | `/api/settings/cookies/upload` | Upload a `cookies.txt` file |
| `POST` | `/api/settings/cookies/youtube` | Bookmarklet cookie sync |
| `GET` | `/health` | Container health check |
| `GET` | `/docs` | Interactive Swagger UI |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 · FastAPI · Uvicorn |
| Downloader | yt-dlp (nightly) · ffmpeg |
| JS runtime | Deno (YouTube signature extraction) |
| Database | SQLite · SQLAlchemy (async) · aiosqlite |
| Auth | JWT (python-jose) · bcrypt (passlib) |
| Frontend | Vanilla HTML · CSS · JS — no build step |
| Container | Docker · Compose |
| CI | GitHub Actions · ruff · pytest |

---

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

cp .env.example .env               # set DATA_ROOT=./data (writable local path)

uvicorn api.main:app --reload --port 8000
```

**Run tests:**

```bash
pytest tests/ -v --asyncio-mode=auto
```

**Lint:**

```bash
ruff check api/ tests/
```

---

## Project Structure

```
yt-Z-downloader/
├── api/
│   ├── main.py              # App factory, CORS, StaticFiles (mounted last)
│   ├── config.py            # Pydantic Settings — .env loader
│   ├── db.py                # Async SQLAlchemy engine, init_db()
│   ├── models.py            # User + Job ORM tables
│   ├── schemas.py           # Pydantic request/response models
│   ├── auth.py              # JWT + bcrypt, get_current_user dependency
│   ├── users.py             # /auth/register · /auth/login
│   ├── download_routes.py   # Download, queue, file serve, cookie endpoints
│   ├── queue.py             # asyncio.Queue · single worker · _jobs dict
│   ├── downloader.py        # yt-dlp Python API wrapper (run_in_executor)
│   └── history.py           # /api/downloads paginated history
├── frontend/
│   ├── index.html           # URL input, metadata preview, submit
│   ├── queue.html           # Live queue, progress bars, Save to PC
│   ├── history.html         # Paginated history table
│   ├── settings.html        # Cookie upload, bookmarklet
│   ├── login.html           # Register / login
│   └── assets/
│       ├── app.js           # Shared helpers: api(), toast(), polling, downloadFile()
│       └── style.css        # Dark theme CSS
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_queue.py
├── .env.example
├── requirements.txt
└── requirements-dev.txt
```

---

## Roadmap

- [ ] WebSocket progress (replace polling)
- [ ] Concurrent multi-worker mode
- [ ] Custom yt-dlp args per download
- [ ] Thumbnail embedding + local media browser
- [ ] PO token / `--impersonate` toggle for YouTube bot detection
- [ ] Admin panel

---

## Contributing

Pull requests are welcome. Please open an issue first for significant changes.

1. Fork and create a feature branch
2. Run `ruff check api/ tests/` and `pytest tests/ -v --asyncio-mode=auto` before pushing
3. Open a PR against `developer`

---

## License

[MIT](LICENSE)
