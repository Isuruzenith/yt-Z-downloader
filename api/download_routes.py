import aiofiles
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.auth import get_current_user
from api.db import get_db
from api import models, schemas, queue, downloader
from api.config import settings

router = APIRouter(prefix="/api", tags=["downloads"])


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
            url=body.url,
            fmt=body.format,
            quality=body.quality,
            playlist=body.playlist,
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
