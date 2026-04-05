from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class DownloadRequest(BaseModel):
    # Core
    url: str
    format: Literal["mp4", "webm", "mp3", "m4a", "mkv", "best"] = "mp4"
    quality: Literal["best", "4k", "1440p", "1080p", "720p", "480p", "audio"] = "best"
    playlist: bool = False

    # Subtitles
    subtitles_langs: list[str] | None = None
    embed_subs: bool = False
    write_thumbnail: bool = False
    embed_thumbnail: bool = False
    write_info_json: bool = False
    embed_metadata: bool = False
    extract_audio: bool = False
    remux: bool = False
    split_chapters: bool = False

    # Proxy & Network
    proxy_url: str | None = None
    rate_limit: int | None = None
    retries: int | None = None
    user_agent: str | None = None
    sponsorblock: Literal["mark", "remove"] | None = None
    power_mode_args: list[str] | None = None

    # Format Selection
    format_sort: str | None = Field(None, description="--format-sort value e.g. 'res,fps,codec'")
    prefer_free_formats: bool = Field(False, description="Prefer free container formats")
    check_formats: bool = Field(False, description="Verify formats are actually downloadable")
    video_codec: str | None = Field(None, description="Preferred video codec: h264/h265/vp9/av1")
    audio_codec: str | None = Field(None, description="Preferred audio codec: aac/opus/mp3/flac")
    merge_output_format: str | None = Field(None, description="Container for merged output: mp4/mkv/webm/mov/avi/flv")

    # Post-Processing
    audio_format: str | None = Field(None, description="Audio codec for extraction: mp3/m4a/flac/opus/vorbis/wav/aac")
    audio_quality: str = Field("192", description="Audio quality: kbps string or 0-10 VBR")
    normalize_audio: bool = Field(False, description="Normalize audio levels via FFmpeg")
    convert_video: str | None = Field(None, description="Convert video to format: mp4/mkv/webm/mov/avi/flv")
    write_description: bool = Field(False, description="Write .description file")
    write_comments: bool = Field(False, description="Write comments to infojson")

    # Subtitles (Extended)
    write_subs: bool = Field(False, description="Write subtitle file")
    write_auto_subs: bool = Field(False, description="Write auto-generated subtitles")
    subtitles_format: str | None = Field(None, description="Subtitle format: srt/vtt/ass/lrc")
    convert_subs: str | None = Field(None, description="Convert subtitles to format")

    # Video Selection
    playlist_items: str | None = Field(None, description="Playlist items e.g. '1,3,5-7'")
    playlist_start: int | None = Field(None, description="Playlist start index")
    playlist_end: int | None = Field(None, description="Playlist end index")
    playlist_reverse: bool = Field(False, description="Reverse playlist order")
    playlist_random: bool = Field(False, description="Random playlist order")
    date_before: str | None = Field(None, description="Only videos uploaded before YYYYMMDD")
    date_after: str | None = Field(None, description="Only videos uploaded after YYYYMMDD")
    min_duration: int | None = Field(None, description="Minimum duration in seconds")
    max_duration: int | None = Field(None, description="Maximum duration in seconds")
    min_views: int | None = Field(None, description="Minimum view count")
    max_views: int | None = Field(None, description="Maximum view count")
    match_title: str | None = Field(None, description="Include only videos matching regex")
    reject_title: str | None = Field(None, description="Exclude videos matching regex")
    break_match_filters: bool = Field(False, description="Stop after first non-matching video")
    skip_livestreams: bool = Field(False, description="Skip live streams")
    age_limit: int | None = Field(None, description="Maximum age limit 0-99")

    # Download Behaviour
    concurrent_fragments: int | None = Field(None, description="Number of concurrent fragment downloads")
    fragment_retries: int | None = Field(None, description="Fragment retry count")
    skip_unavailable_fragments: bool = Field(False, description="Skip unavailable fragments")
    buffersize: str | None = Field(None, description="Download buffer size e.g. '1024'")
    http_chunk_size: str | None = Field(None, description="HTTP chunk size for chunked downloads")
    ignore_errors: bool = Field(False, description="Continue on download errors")
    download_archive: str | None = Field(None, description="Path to download archive file")
    overwrites: bool | None = Field(None, description="True=overwrite, False=never overwrite, None=default")
    keep_fragments: bool = Field(False, description="Keep downloaded fragments")
    sleep_requests: float | None = Field(None, description="Seconds to sleep between requests")
    sleep_interval: float | None = Field(None, description="Seconds to sleep before each download")
    downloader: str | None = Field(None, description="External downloader: native/ffmpeg/aria2c/curl/wget")
    downloader_args: str | None = Field(None, description="Arguments for external downloader")

    # Network & Authentication
    source_address: str | None = Field(None, description="Source IP address to bind to")
    force_ipv4: bool = Field(False, description="Force IPv4 connections")
    force_ipv6: bool = Field(False, description="Force IPv6 connections")
    geo_bypass: bool = Field(False, description="Bypass geographic restrictions")
    geo_bypass_country: str | None = Field(None, description="2-letter country code for geo bypass")
    socket_timeout: int | None = Field(None, description="Socket timeout in seconds")
    custom_headers: dict[str, str] = Field(default_factory=dict, description="Custom HTTP headers")
    cookies_from_browser: str | None = Field(None, description="Load cookies from browser: chrome/firefox/edge/safari/brave")
    username: str | None = Field(None, description="Login username")
    password: str | None = Field(None, description="Login password")
    twofactor: str | None = Field(None, description="Two-factor auth code")
    netrc: bool = Field(False, description="Use .netrc for authentication")
    no_check_certificates: bool = Field(False, description="Skip HTTPS certificate validation")
    prefer_insecure: bool = Field(False, description="Prefer HTTP over HTTPS")

    # SponsorBlock
    sponsorblock_categories: list[str] = Field(default_factory=list, description="SponsorBlock categories to process")
    sponsorblock_api_url: str = Field("https://sponsor.ajay.app", description="SponsorBlock API URL")
    sponsorblock_chapter_title: str | None = Field(None, description="Chapter title template for marked segments")

    # Output Template
    restrict_filenames: bool = Field(False, description="Restrict filenames to ASCII")
    windows_filenames: bool = Field(False, description="Ensure filenames are Windows-compatible")
    trim_filenames: int | None = Field(None, description="Trim filename to N characters")
    no_part_files: bool = Field(False, description="Do not use .part files during download")
    outtmpl: str | None = Field(None, description="Output filename template")

    # Extractor
    extractor_args: dict[str, dict] = Field(default_factory=dict, description="Extractor-specific arguments")
    extract_flat: str | bool = Field(False, description="Extract flat playlist: True or 'in_playlist'")


class JobResponse(BaseModel):
    id: str
    status: str
    progress: float
    url: str
    format: str
    quality: str
    title: str | None
    filepath: str | None
    error_msg: str | None


class FormatInfo(BaseModel):
    format_id: str
    ext: str
    resolution: str | None
    fps: float | None
    tbr: float | None
    vcodec: str | None
    acodec: str | None
    filesize: int | None
    format_note: str | None
    dynamic_range: str | None
    audio_channels: int | None
    asr: int | None
    is_video: bool
    is_audio: bool
