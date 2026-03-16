from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    secret_key: str = "change-me-in-production"
    download_root: Path = Path("/downloads")
    cookies_root: Path = Path("/cookies")
    data_root: Path = Path("/data")
    max_queue_size: int = 50
    max_retries: int = 3
    default_format: str = "mp4"
    ytdlp_channel: str = "nightly"
    js_runtime: str = "deno"
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
