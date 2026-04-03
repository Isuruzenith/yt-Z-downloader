from pydantic import BaseModel, EmailStr
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
    url: str
    format: Literal["mp4", "webm", "mp3", "m4a", "mkv", "best"] = "mp4"
    quality: Literal["best", "4k", "1440p", "1080p", "720p", "480p", "audio"] = "best"
    playlist: bool = False

    subtitles_langs: list[str] | None = None
    embed_subs: bool = False
    write_thumbnail: bool = False
    embed_thumbnail: bool = False
    write_info_json: bool = False
    embed_metadata: bool = False
    extract_audio: bool = False
    remux: bool = False
    split_chapters: bool = False

    proxy_url: str | None = None
    rate_limit: int | None = None
    retries: int | None = None
    user_agent: str | None = None
    sponsorblock: Literal["mark", "remove"] | None = None
    power_mode_args: list[str] | None = None


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
