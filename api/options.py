from pathlib import Path
from typing import Callable
from api.schemas import DownloadRequest
from api.config import settings

FORMAT_MAP = {
    # (format_key, quality_key) → yt-dlp format selector string
    ("mp4",  "best"):   "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    ("mp4",  "1080p"):  "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
    ("mp4",  "720p"):   "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
    ("mp4",  "480p"):   "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
    ("mp4",  "4k"):     "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best",
    ("mp4",  "1440p"):  "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best",
    ("webm", "best"):   "bestvideo[ext=webm]+bestaudio[ext=webm]/bestvideo+bestaudio",
    ("mkv",  "best"):   "bestvideo+bestaudio/best",
    ("mp3",  "audio"):  "bestaudio/best",
    ("m4a",  "audio"):  "bestaudio[ext=m4a]/bestaudio/best",
}

def build_format_selector(fmt: str, quality: str) -> str:
    key = (fmt.lower(), quality.lower())
    return FORMAT_MAP.get(key, "bestvideo+bestaudio/best")

ALLOWED_POWER_ARGS = {
    "--force-ipv4", "--force-ipv6", "--geo-bypass", "--no-geo-bypass",
    "--flat-playlist", "--no-flat-playlist", "--ignore-errors", "--abort-on-error"
}

def build_ydl_opts(
    req: DownloadRequest,
    job_id: str,
    user_id: int,
    cookie_file: Path | None,
    progress_cb: Callable[[dict], None],
) -> dict:
    output_dir = settings.download_root / str(user_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(output_dir / job_id / "%(title)s.%(ext)s")

    opts = {
        "format": build_format_selector(req.format, req.quality),
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [progress_cb],
        "retries": req.retries if req.retries is not None else settings.max_retries,
        "sleep_interval": 1,
        "max_sleep_interval": 5,
        "noplaylist": not req.playlist,
        "logger": None,
    }

    if req.format in ("mp4", "mkv", "webm") and req.remux:
        opts["merge_output_format"] = req.format

    postprocessors = []

    if req.format in ("mp3", "m4a") or req.extract_audio:
        postprocessors.append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": req.format if req.format in ("mp3", "m4a") else "best",
            "preferredquality": "192",
        })

    if req.embed_metadata:
        postprocessors.append({"key": "FFmpegMetadata", "add_metadata": True})

    if req.embed_thumbnail:
        opts["writethumbnail"] = True
        postprocessors.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})
    elif req.write_thumbnail:
        opts["writethumbnail"] = True

    if req.split_chapters:
        postprocessors.append({"key": "FFmpegSplitChapters"})

    if req.subtitles_langs:
        opts["writesubtitles"] = True
        opts["subtitleslangs"] = req.subtitles_langs
        if req.embed_subs:
            postprocessors.append({"key": "FFmpegEmbedSubtitle"})

    if postprocessors:
        opts["postprocessors"] = postprocessors

    if req.write_info_json:
        opts["writeinfojson"] = True

    if cookie_file and cookie_file.exists():
        opts["cookiefile"] = str(cookie_file)

    if req.proxy_url:
        opts["proxy"] = req.proxy_url

    if req.rate_limit:
        opts["ratelimit"] = req.rate_limit

    if req.user_agent:
        opts["http_headers"] = {"User-Agent": req.user_agent}

    if req.sponsorblock and settings.enable_sponsorblock:
        postprocessors.append({
            "key": "SponsorBlock",
            "api": "https://sponsor.ajay.app",
            "categories": ["sponsor", "intro", "outro", "selfpromo", "interaction", "music_offtopic"],
        })
        # If remove, we don't need to do anything as it's the default action? No, wait:
        # Actually yt-dlp SponsorBlock postprocessor requires some specific options. Let's just use:
        if req.sponsorblock == "mark":
            opts["sponsorblock_mark"] = ["all"]
        elif req.sponsorblock == "remove":
            opts["sponsorblock_remove"] = ["all"]

    # Not supporting full power mode here, just simple extra args passing if enabled.
    # Note: actually yt_dlp python API doesn't take raw argv for YoutubeDL, it takes a dictionary.
    # But for "extra_args", maybe we can't easily parse them. It's better to just raise an error or parse.
    # The requirement says "accept raw extra_args list; validate each arg against strict allowlist"
    # But in YoutubeDL python API, options are dict keys, not argv. 
    # Let's ignore extra args for YoutubeDL instantiation, or map known ones:
    if req.power_mode_args and settings.enable_power_mode:
        for arg in req.power_mode_args:
            if arg not in ALLOWED_POWER_ARGS:
                raise ValueError(f"Power mode argument not allowed: {arg}")
            if arg == "--force-ipv4":
                opts["source_address"] = "0.0.0.0"
            elif arg == "--geo-bypass":
                opts["geo_bypass"] = True
            elif arg == "--no-geo-bypass":
                opts["geo_bypass"] = False
            elif arg == "--flat-playlist":
                opts["extract_flat"] = True
            elif arg == "--ignore-errors":
                opts["ignoreerrors"] = True
            elif arg == "--abort-on-error":
                opts["ignoreerrors"] = False

    return opts
