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
