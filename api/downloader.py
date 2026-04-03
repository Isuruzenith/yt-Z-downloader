import asyncio
from pathlib import Path
from typing import Callable
import yt_dlp
from api.config import settings
from api.schemas import DownloadRequest
from api.options import build_ydl_opts

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


class JobLogger:
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        # clear file if exists
        if self.log_file.exists():
            self.log_file.write_text("")

    def _write(self, msg: str):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    def debug(self, msg: str):
        self._write(msg)

    def warning(self, msg: str):
        self._write(f"WARNING: {msg}")

    def error(self, msg: str):
        self._write(f"ERROR: {msg}")



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
    req: DownloadRequest,
    job_id: str,
    user_id: int,
    cookie_file: Path | None,
    progress_cb: Callable[[dict], None],
) -> str | None:
    """Non-blocking download. Returns filepath on completion."""
    opts = build_ydl_opts(req, job_id, user_id, cookie_file, progress_cb)
    log_file = settings.download_root / str(user_id) / job_id / 'job.log'
    opts['logger'] = JobLogger(log_file)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download_sync, opts, req.url)
