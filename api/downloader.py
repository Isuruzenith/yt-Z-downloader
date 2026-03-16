import asyncio
from pathlib import Path
from typing import Callable
import yt_dlp
from api.config import settings

# ── Format string builders ────────────────────────────────────────────────────

FORMAT_MAP = {
    # (format_key, quality_key) → yt-dlp format selector string
    ("mp4",  "best"):   "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    ("mp4",  "1080p"):  "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
    ("mp4",  "720p"):   "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
    ("mp4",  "480p"):   "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
    ("mp4",  "4k"):     "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best",
    ("mp4",  "1440p"):  "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best",
    ("webm", "best"):   "bestvideo[ext=webm]+bestaudio[ext=webm]/bestvideo+bestaudio",
    ("mp3",  "audio"):  "bestaudio/best",
    ("m4a",  "audio"):  "bestaudio[ext=m4a]/bestaudio/best",
}


def build_format_selector(fmt: str, quality: str) -> str:
    key = (fmt.lower(), quality.lower())
    return FORMAT_MAP.get(key, "bestvideo+bestaudio/best")


# ── Info extraction (metadata preview) ───────────────────────────────────────

def _extract_info_sync(url: str, cookie_file: Path | None) -> dict:
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
    }
    if cookie_file and cookie_file.exists():
        opts["cookiefile"] = str(cookie_file)

    with yt_dlp.YoutubeDL(opts) as ydl:
        raw = ydl.extract_info(url, download=False)
        return yt_dlp.YoutubeDL.sanitize_info(raw)


async def extract_info(url: str, cookie_file: Path | None = None) -> dict:
    """Non-blocking metadata fetch. Returns sanitized info dict."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _extract_info_sync, url, cookie_file)


# ── Download execution ───────────────────────────────────────────────────────

def _build_ydl_opts(
    job_id: str,
    user_id: int,
    fmt: str,
    quality: str,
    playlist: bool,
    cookie_file: Path | None,
    progress_cb: Callable[[dict], None],
) -> dict:
    output_dir = settings.download_root / str(user_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    outtmpl = str(output_dir / job_id / "%(title)s.%(ext)s")

    opts: dict = {
        "format": build_format_selector(fmt, quality),
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [progress_cb],
        "retries": settings.max_retries,
        "sleep_interval": 1,
        "max_sleep_interval": 5,
        "noplaylist": not playlist,
        "merge_output_format": fmt if fmt in ("mp4", "mkv", "webm") else None,
        **({"postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": fmt}]}
           if fmt in ("mp3", "m4a") else {}),
    }

    if cookie_file and cookie_file.exists():
        opts["cookiefile"] = str(cookie_file)

    return opts


def _download_sync(opts: dict, url: str) -> str | None:
    """Synchronous yt-dlp download. Returns final filepath or None."""
    final_path: list[str] = []

    orig_hooks = opts.get("postprocessor_hooks", [])

    def _capture_path(d: dict):
        if d.get("status") == "finished" and d.get("info_dict", {}).get("filepath"):
            final_path.append(d["info_dict"]["filepath"])

    opts["postprocessor_hooks"] = orig_hooks + [_capture_path]

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    return final_path[-1] if final_path else None


async def run_download(
    job_id: str,
    user_id: int,
    url: str,
    fmt: str,
    quality: str,
    playlist: bool,
    cookie_file: Path | None,
    progress_cb: Callable[[dict], None],
) -> str | None:
    """Non-blocking download. Returns filepath on completion."""
    opts = _build_ydl_opts(job_id, user_id, fmt, quality, playlist, cookie_file, progress_cb)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download_sync, opts, url)
