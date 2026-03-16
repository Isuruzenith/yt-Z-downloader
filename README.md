# yt-Z-Downloader

Self-hosted video downloader powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).
Free forever. No accounts. No tracking.

[![CI](https://github.com/Isuruzenith/yt-Z-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/Isuruzenith/yt-Z-downloader/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue)](https://github.com/Isuruzenith/yt-Z-downloader/pkgs/container/yt-z-downloader)

## Quick start

```bash
git clone https://github.com/Isuruzenith/yt-Z-downloader.git
cd yt-Z-downloader
cp .env.example .env
docker compose up
```

Open **http://localhost:8080**

## Features

- 1000+ supported sites via yt-dlp (YouTube, TikTok, Vimeo, Twitter, and more)
- Queue system — submit multiple URLs, track progress in real time
- Format picker — MP4, MKV, MP3, M4A, or best available
- Quality selector — 4K, 1080p, 720p, 480p, audio only
- Cookie auth — paste `cookies.json` for age-restricted or member content
- Minimal web UI — no JavaScript framework, works on mobile
- Optional API key auth for shared/exposed deployments
- REST API with auto-generated docs at `/docs`

## Screenshots

> TODO: add screenshots after first stable release

## Configuration

All settings via environment variables (copy `.env.example` to `.env`):

| Variable | Default | Description |
|---|---|---|
| `DOWNLOAD_PATH` | `/downloads` | Where files are saved |
| `COOKIES_PATH` | `/cookies` | Directory containing `cookies.json` |
| `DATA_PATH` | `/data` | History database location |
| `MAX_QUEUE_SIZE` | `50` | Max queued + active jobs |
| `MAX_RETRIES` | `3` | Retry attempts on download failure |
| `DEFAULT_FORMAT` | `mp4` | Default output format |
| `API_KEY` | _(empty)_ | Set to require `X-API-Key` header. Empty = no auth |
| `PORT` | `8080` | Exposed port |

## Cookie setup

To download age-restricted or member-only content:

1. Install the [cookies.txt browser extension](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
2. Export cookies from YouTube (or relevant site) as `cookies.json`
3. Place the file in `./cookies/cookies.json`
4. Or upload it via the Settings page in the UI

## Development

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python -m uvicorn api.main:app --reload --port 8080
```

Run tests:

```bash
pytest tests/ -q
```

Lint:

```bash
ruff check api/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) — free to use, self-host, fork, and modify.
