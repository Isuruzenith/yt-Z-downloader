import asyncio
import uuid
import logging
from datetime import datetime
from typing import Any
from pathlib import Path
from api import downloader
from api.config import settings
from api.db import AsyncSessionLocal
from api import models

logger = logging.getLogger(__name__)

# In-memory job registry: job_id → job dict
# Persisted to DB, but kept in-memory for O(1) live progress reads
_jobs: dict[str, dict[str, Any]] = {}
_queue: asyncio.Queue = asyncio.Queue(maxsize=settings.max_queue_size)
_worker_task: asyncio.Task | None = None


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def get_user_jobs(user_id: int) -> list[dict]:
    return [j for j in _jobs.values() if j["user_id"] == user_id]


async def enqueue(
    user_id: int,
    url: str,
    fmt: str,
    quality: str,
    playlist: bool,
    cookie_file: Path | None,
) -> str:
    if _queue.full():
        raise RuntimeError("Queue is full")

    job_id = str(uuid.uuid4())
    job: dict[str, Any] = {
        "id": job_id,
        "user_id": user_id,
        "url": url,
        "format": fmt,
        "quality": quality,
        "playlist": playlist,
        "cookie_file": cookie_file,
        "status": "queued",
        "progress": 0.0,
        "title": None,
        "filepath": None,
        "error_msg": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    _jobs[job_id] = job

    async with AsyncSessionLocal() as db:
        db.add(models.Job(
            id=job_id, user_id=user_id, url=url,
            format=fmt, quality=quality, status="queued",
        ))
        await db.commit()

    await _queue.put(job_id)
    return job_id


async def cancel_job(job_id: str, user_id: int) -> bool:
    job = _jobs.get(job_id)
    if not job or job["user_id"] != user_id:
        return False
    if job["status"] == "queued":
        job["status"] = "cancelled"
        return True
    # Running jobs cannot be cancelled mid-flight (yt-dlp has no clean abort)
    return False


async def _process_job(job_id: str):
    job = _jobs[job_id]

    if job["status"] == "cancelled":
        return

    job["status"] = "running"

    def progress_cb(d: dict):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            job["progress"] = round((downloaded / total * 100), 1) if total else 0.0
        elif d["status"] == "finished":
            job["progress"] = 100.0

    try:
        filepath = await downloader.run_download(
            job_id=job_id,
            user_id=job["user_id"],
            url=job["url"],
            fmt=job["format"],
            quality=job["quality"],
            playlist=job["playlist"],
            cookie_file=job["cookie_file"],
            progress_cb=progress_cb,
        )
        job["status"] = "done"
        job["filepath"] = filepath
        job["progress"] = 100.0
    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        job["status"] = "error"
        job["error_msg"] = str(exc)

    # Persist result to DB
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(models.Job).where(models.Job.id == job_id))
        db_job = result.scalar_one_or_none()
        if db_job:
            db_job.status = job["status"]
            db_job.filepath = job.get("filepath")
            db_job.error_msg = job.get("error_msg")
            db_job.finished_at = datetime.utcnow()
            await db.commit()


async def _worker():
    """Single sequential worker — processes one job at a time."""
    while True:
        job_id = await _queue.get()
        try:
            await _process_job(job_id)
        except Exception:
            logger.exception("Unhandled error in worker for job %s", job_id)
        finally:
            _queue.task_done()


def start_worker():
    global _worker_task
    _worker_task = asyncio.create_task(_worker())
