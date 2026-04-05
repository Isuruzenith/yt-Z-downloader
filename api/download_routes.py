import aiofiles
import json
import shutil
import subprocess
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.auth import get_current_user
from api.db import get_db
from api import models, schemas, queue, downloader
from api.config import settings

router = APIRouter(prefix="/api", tags=["downloads"])

DEFAULTS_FILE_NAME = "download_defaults.json"


def get_user_defaults_path(user_id: int) -> Path:
    path = settings.download_root / str(user_id) / DEFAULTS_FILE_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# ── Video info preview ────────────────────────────────────────────────────────

@router.get("/info")
async def get_info(
    url: str,
    current_user: models.User = Depends(get_current_user),
):
    cookie_file = settings.cookies_root / str(current_user.id) / "cookies.txt"
    try:
        info = await downloader.extract_info(url, cookie_file)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "formats": [
            {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "height": f.get("height"),
                "filesize": f.get("filesize"),
                "vcodec": f.get("vcodec"),
                "acodec": f.get("acodec"),
            }
            for f in (info.get("formats") or [])
        ],
    }


# ── Download queue ────────────────────────────────────────────────────────────

@router.post("/download", response_model=schemas.JobResponse)
async def start_download(
    body: schemas.DownloadRequest,
    current_user: models.User = Depends(get_current_user),
):
    cookie_file = settings.cookies_root / str(current_user.id) / "cookies.txt"
    try:
        job_id = await queue.enqueue(
            user_id=current_user.id,
            req=body,
            cookie_file=cookie_file if cookie_file.exists() else None,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))
    return queue.get_job(job_id)


@router.get("/queue")
async def get_queue(current_user: models.User = Depends(get_current_user)):
    return queue.get_user_jobs(current_user.id)


@router.delete("/queue/{job_id}")
async def cancel(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
):
    cancelled = await queue.cancel_job(job_id, current_user.id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Job not found or already running")
    return {"cancelled": True}


@router.get("/queue/{job_id}/file")
async def get_file(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Try in-memory first (live jobs)
    job = queue.get_job(job_id)
    if job:
        if job["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Job not found")
        filepath = job.get("filepath")
    else:
        # Fall back to DB (jobs survive container restart in history)
        result = await db.execute(
            select(models.Job).where(
                models.Job.id == job_id,
                models.Job.user_id == current_user.id,
            )
        )
        db_job = result.scalar_one_or_none()
        if not db_job:
            raise HTTPException(status_code=404, detail="Job not found")
        filepath = db_job.filepath

    if not filepath:
        raise HTTPException(status_code=400, detail="No file available for this job")

    path = Path(filepath)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File no longer exists on disk")

    return FileResponse(path, filename=path.name, media_type="application/octet-stream")


# ── Cookie management ─────────────────────────────────────────────────────────

@router.post("/settings/cookies/upload")
async def upload_cookies(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    cookie_dir = settings.cookies_root / str(current_user.id)
    cookie_dir.mkdir(parents=True, exist_ok=True)
    dest = cookie_dir / "cookies.txt"
    async with aiofiles.open(dest, "wb") as f:
        await f.write(await file.read())
    return {"message": "Cookies uploaded successfully"}


@router.post("/settings/cookies/youtube")
async def sync_youtube_cookies(
    body: dict,
    current_user: models.User = Depends(get_current_user),
):
    """Receives cookies from the YouTube bookmarklet and writes Netscape format."""
    cookie_dir = settings.cookies_root / str(current_user.id)
    cookie_dir.mkdir(parents=True, exist_ok=True)
    dest = cookie_dir / "cookies.txt"

    lines = ["# Netscape HTTP Cookie File\n"]
    for c in body.get("cookies", []):
        domain = c.get("domain", ".youtube.com")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        secure = "TRUE" if c.get("secure") else "FALSE"
        expiry = int(c.get("expirationDate", 0))
        name = c.get("name", "")
        value = c.get("value", "")
        path = c.get("path", "/")
        lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")

    async with aiofiles.open(dest, "w") as f:
        await f.writelines(lines)

    return {"message": "YouTube cookies synced"}


@router.get("/queue/{job_id}/log")
async def get_log(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log_path = settings.download_root / str(current_user.id) / job_id / "job.log"
    if not log_path.exists():
        raise HTTPException(status_code=404, detail="Log not found")
    
    # Returning as text
    return FileResponse(log_path, media_type="text/plain")


@router.get("/queue/{job_id}/info")
async def get_info_json(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_dir = settings.download_root / str(current_user.id) / job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job directory not found")
    
    # Find the .info.json file
    for p in job_dir.glob("*.info.json"):
        return FileResponse(p, media_type="application/json")
    
    raise HTTPException(status_code=404, detail="Info JSON not found")


# ── List formats ───────────────────────────────────────────────────────────────

@router.get("/formats")
async def list_formats(
    url: str = Query(..., description="URL to inspect"),
    current_user: models.User = Depends(get_current_user),
):
    """Return all available formats for a URL without downloading."""
    cookie_file = settings.cookies_root / str(current_user.id) / "cookies.txt"
    try:
        info = await downloader.extract_info(url, cookie_file)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to extract info: {e}")

    formats = info.get("formats", [])

    def classify(f):
        vcodec = f.get("vcodec") or "none"
        acodec = f.get("acodec") or "none"
        return {
            "format_id": f.get("format_id", ""),
            "ext": f.get("ext", ""),
            "resolution": f.get("resolution") or (
                f"{f['width']}x{f['height']}" if f.get("width") and f.get("height") else "audio only"
            ),
            "fps": f.get("fps"),
            "tbr": f.get("tbr"),
            "vcodec": None if vcodec == "none" else vcodec,
            "acodec": None if acodec == "none" else acodec,
            "filesize": f.get("filesize") or f.get("filesize_approx"),
            "format_note": f.get("format_note"),
            "dynamic_range": f.get("dynamic_range"),
            "audio_channels": f.get("audio_channels"),
            "asr": f.get("asr"),
            "is_video": vcodec != "none",
            "is_audio": acodec != "none",
            "quality": f.get("quality", 0),
        }

    return {
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "formats": [classify(f) for f in formats],
    }


# ── Settings: defaults ───────────────────────────────────────────────────────

@router.get("/settings/defaults")
async def get_defaults(current_user: models.User = Depends(get_current_user)):
    """Get user default download options."""
    path = get_user_defaults_path(current_user.id)
    if path.exists():
        return json.loads(path.read_text())
    return {}


@router.post("/settings/defaults")
async def save_defaults(
    defaults: dict,
    current_user: models.User = Depends(get_current_user),
):
    """Save user default download options."""
    path = get_user_defaults_path(current_user.id)
    path.write_text(json.dumps(defaults, indent=2))
    return {"message": "Defaults saved"}


# ── Settings: tool versions ───────────────────────────────────────────────────

@router.get("/settings/yt-dlp-version")
async def get_tool_versions(current_user: models.User = Depends(get_current_user)):
    """Return yt-dlp, ffmpeg, and other tool versions."""
    def check_tool(name: str) -> dict:
        path = shutil.which(name)
        if not path:
            return {"available": False, "version": None, "path": None}
        try:
            result = subprocess.run(
                [name, "--version"], capture_output=True, text=True, timeout=5
            )
            return {
                "available": True,
                "version": result.stdout.strip().splitlines()[0] if result.returncode == 0 else "unknown",
                "path": path,
            }
        except Exception:
            return {"available": True, "version": "unknown", "path": path}

    import yt_dlp
    return {
        "yt_dlp": {"available": True, "version": yt_dlp.version.__version__, "path": shutil.which("yt-dlp")},
        "ffmpeg": check_tool("ffmpeg"),
        "ffprobe": check_tool("ffprobe"),
        "aria2c": check_tool("aria2c"),
        "curl": check_tool("curl"),
        "wget": check_tool("wget"),
    }
