from pathlib import Path
from typing import Callable
from api.schemas import DownloadRequest
from api.config import settings

FORMAT_MAP = {
    ("mp4", "best"): "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    ("mp4", "1080p"): "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
    ("mp4", "720p"): "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
    ("mp4", "480p"): "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
    ("mp4", "4k"): "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best",
    ("mp4", "1440p"): "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best",
    ("webm", "best"): "bestvideo[ext=webm]+bestaudio[ext=webm]/bestvideo+bestaudio",
    ("mkv", "best"): "bestvideo+bestaudio/best",
    ("mp3", "audio"): "bestaudio/best",
    ("m4a", "audio"): "bestaudio[ext=m4a]/bestaudio/best",
}

ALLOWED_POWER_ARGS = {
    "--force-ipv4", "--force-ipv6", "--geo-bypass", "--no-geo-bypass",
    "--flat-playlist", "--no-flat-playlist", "--ignore-errors", "--abort-on-error"
}


def build_format_selector(req: DownloadRequest) -> str:
    """Build yt-dlp format selector string from request fields."""
    if req.video_codec or req.audio_codec:
        parts = []
        if req.quality != "best":
            if req.quality == "4k":
                parts.append("height<=2160")
            elif req.quality == "1440p":
                parts.append("height<=1440")
            elif req.quality == "1080p":
                parts.append("height<=1080")
            elif req.quality == "720p":
                parts.append("height<=720")
            elif req.quality == "480p":
                parts.append("height<=480")
            elif req.quality == "audio":
                pass
            else:
                parts.append(f"height<={req.quality}")
        if req.video_codec:
            parts.append(f"vcodec~{req.video_codec}")
        if req.audio_codec:
            parts.append(f"acodec~{req.audio_codec}")
        if req.format != "best":
            parts.append(f"ext={req.format}")
        return "+".join(parts) if parts else "bestvideo+bestaudio/best"

    key = (req.format.lower(), req.quality.lower())
    return FORMAT_MAP.get(key, "bestvideo+bestaudio/best")


def build_match_filter(req: DownloadRequest) -> str | None:
    """Combine all filter predicates into a single yt-dlp match_filter string."""
    parts = []
    if req.min_duration is not None:
        parts.append(f"duration >= {req.min_duration}")
    if req.max_duration is not None:
        parts.append(f"duration <= {req.max_duration}")
    if req.min_views is not None:
        parts.append(f"view_count >= {req.min_views}")
    if req.max_views is not None:
        parts.append(f"view_count <= {req.max_views}")
    if req.match_title:
        parts.append(f"title ~= (?i){req.match_title}")
    if req.reject_title:
        parts.append(f"title !~= (?i){req.reject_title}")
    if req.skip_livestreams:
        parts.append("!is_live")
    if req.age_limit is not None:
        parts.append(f"age_limit <=? {req.age_limit}")
    return " & ".join(parts) if parts else None


def build_postprocessors(req: DownloadRequest) -> list[dict]:
    """Build ordered list of yt-dlp postprocessor dicts from request fields."""
    pps = []

    if req.extract_audio or req.format in ("mp3", "m4a", "flac", "opus", "vorbis", "wav", "aac"):
        pps.append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": req.audio_format or (req.format if req.format in ("mp3", "m4a", "flac", "opus", "vorbis", "wav", "aac") else "best"),
            "preferredquality": req.audio_quality,
        })
    elif req.convert_video:
        pps.append({"key": "FFmpegVideoConvertor", "preferedformat": req.convert_video})
    elif req.remux and req.merge_output_format:
        pps.append({"key": "FFmpegVideoRemuxer", "preferedformat": req.merge_output_format})

    if req.split_chapters:
        pps.append({"key": "FFmpegSplitChapters"})

    if req.convert_subs:
        pps.append({"key": "FFmpegSubtitlesConvertor", "format": req.convert_subs})
    if req.embed_subs and req.write_subs:
        pps.append({"key": "FFmpegEmbedSubtitle", "already_have_subtitle": False})

    if req.embed_metadata:
        pps.append({"key": "FFmpegMetadata", "add_metadata": True, "add_chapters": True, "add_infojson": False})

    if req.embed_thumbnail:
        pps.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

    if req.normalize_audio:
        pps.append({"key": "FFmpegNormalizeAudio"})

    if req.sponsorblock and req.sponsorblock != "none" and settings.enable_sponsorblock:
        pps.append({
            "key": "SponsorBlock",
            "api": req.sponsorblock_api_url,
            "categories": req.sponsorblock_categories or ["sponsor"],
            "when": "after_filter",
        })
        if req.sponsorblock == "remove":
            pps.append({
                "key": "ModifyChapters",
                "remove_sponsor_segments": req.sponsorblock_categories or ["sponsor"],
                "sponsorblock_chapter_title": req.sponsorblock_chapter_title or "[SponsorBlock]: %(category_names)l",
                "force_keyframes": False,
            })

    return pps


def _parse_rate(rate_str: str | None) -> int | None:
    """Parse '1M', '500K', '2G' to bytes per second."""
    if not rate_str:
        return None
    rate_str = rate_str.strip().upper()
    multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3}
    for suffix, mult in multipliers.items():
        if rate_str.endswith(suffix):
            try:
                return int(float(rate_str[:-1]) * mult)
            except ValueError:
                return None
    try:
        return int(rate_str)
    except ValueError:
        return None


def build_ydl_opts(
    req: DownloadRequest,
    job_id: str,
    user_id: int,
    cookie_file: Path | None,
    progress_cb: Callable[[dict], None],
) -> dict:
    output_dir = settings.download_root / str(user_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = req.outtmpl or str(output_dir / job_id / "%(title)s.%(ext)s")

    opts = {
        "format": build_format_selector(req),
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [progress_cb],
        "retries": req.retries if req.retries is not None else settings.max_retries,
        "noplaylist": not req.playlist,
        "logger": None,
    }

    opts["merge_output_format"] = req.merge_output_format or (req.format if req.format in ("mp4", "mkv", "webm", "mov", "avi", "flv") else None)
    opts["prefer_free_formats"] = req.prefer_free_formats

    opts["playliststart"] = req.playlist_start
    opts["playlistend"] = req.playlist_end
    opts["playlist_items"] = req.playlist_items
    opts["playlistreverse"] = req.playlist_reverse
    opts["playlist_random"] = req.playlist_random
    opts["extract_flat"] = req.extract_flat

    opts["datebefore"] = req.date_before
    opts["dateafter"] = req.date_after

    opts["match_filter"] = build_match_filter(req)
    opts["break_match_filters"] = req.break_match_filters

    opts["age_limit"] = req.age_limit

    opts["fragment_retries"] = req.fragment_retries
    opts["skip_unavailable_fragments"] = req.skip_unavailable_fragments
    opts["concurrent_fragment_downloads"] = req.concurrent_fragments
    opts["buffersize"] = req.buffersize
    opts["http_chunk_size"] = req.http_chunk_size
    opts["sleep_requests"] = req.sleep_requests
    opts["sleep_interval"] = req.sleep_interval
    opts["max_sleep_interval"] = (req.sleep_interval or 1) * 2 if req.sleep_interval else 5
    opts["ratelimit"] = _parse_rate(str(req.rate_limit)) if req.rate_limit else None
    opts["ignoreerrors"] = req.ignore_errors
    opts["download_archive"] = req.download_archive
    opts["overwrites"] = req.overwrites
    opts["keepfragments"] = req.keep_fragments
    opts["nopart"] = req.no_part_files

    opts["external_downloader"] = req.downloader
    opts["external_downloader_args"] = req.downloader_args

    opts["writesubtitles"] = req.write_subs
    opts["writeautomaticsub"] = req.write_auto_subs
    opts["subtitleslangs"] = req.subtitles_langs or []
    opts["subtitlesformat"] = req.subtitles_format

    opts["writethumbnail"] = req.write_thumbnail or req.embed_thumbnail

    opts["writeinfojson"] = req.write_info_json
    opts["writedescription"] = req.write_description
    opts["writecomments"] = req.write_comments

    opts["restrictfilenames"] = req.restrict_filenames
    opts["windowsfilenames"] = req.windows_filenames
    opts["trim_filenames"] = req.trim_filenames

    opts["proxy"] = req.proxy_url
    opts["socket_timeout"] = req.socket_timeout
    opts["geo_bypass"] = req.geo_bypass
    opts["geo_bypass_country"] = req.geo_bypass_country
    opts["nocheckcertificate"] = req.no_check_certificates
    opts["prefer_insecure"] = req.prefer_insecure

    opts["username"] = req.username
    opts["password"] = req.password
    opts["twofactor"] = req.twofactor
    opts["usenetrc"] = req.netrc

    opts["cookiesfrombrowser"] = (req.cookies_from_browser, None, None, None) if req.cookies_from_browser else None

    opts["extractor_args"] = req.extractor_args or {}

    opts["format_sort"] = req.format_sort.split(",") if req.format_sort else None
    opts["check_formats"] = req.check_formats or None

    if req.force_ipv4:
        opts["source_address"] = "0.0.0.0"
    elif req.force_ipv6:
        opts["source_address"] = "::"
    elif req.source_address:
        opts["source_address"] = req.source_address

    headers = dict(req.custom_headers or {})
    if req.user_agent:
        headers["User-Agent"] = req.user_agent
    if headers:
        opts["http_headers"] = headers

    if cookie_file and cookie_file.exists():
        opts["cookiefile"] = str(cookie_file)

    pps = build_postprocessors(req)
    if pps:
        opts["postprocessors"] = pps

    opts = {k: v for k, v in opts.items() if v is not None}

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
