import asyncio
import uuid
import logging
from datetime import datetime
from typing import Any
from pathlib import Path
from api import downloader
from api.ws import manager
from api.config import settings
from api.db import AsyncSessionLocal
from api import models
from api.schemas import DownloadRequest

logger = logging.getLogger(__name__)

# In-memory job registry: job_id → job dict
# Persisted to DB, but kept in-memory for O(1) live progress reads
_jobs: dict[str, dict[str, Any]] = {}
_queue: asyncio.Queue = asyncio.Queue(maxsize=settings.max_queue_size)
_worker_task: asyncio.Task | None = None




_main_loop = None

def get_main_loop():
    global _main_loop
    if _main_loop is None:
        try:
            _main_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
    return _main_loop

def _notify_update(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        return
        
    loop = get_main_loop()
    if not loop:
        return
        
    safe_job = {
        "id": job["id"],
        "status": job["status"],
        "progress": job["progress"],
        "title": job["title"],
        "url": job["url"],
        "format": job["format"],
        "quality": job["quality"],
        "filepath": job["filepath"],
        "error_msg": job["error_msg"]
    }
    
    def send():
        loop.create_task(manager.broadcast_to_user(job["user_id"], safe_job))
        
    loop.call_soon_threadsafe(send)


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def get_user_jobs(user_id: int) -> list[dict]:
    return [j for j in _jobs.values() if j["user_id"] == user_id]


async def enqueue(
    user_id: int,
    req: DownloadRequest,
    cookie_file: Path | None,
) -> str:
    if _queue.full():
        raise RuntimeError("Queue is full")

    job_id = str(uuid.uuid4())
    job: dict[str, Any] = {
        "id": job_id,
        "user_id": user_id,
        "url": req.url,
        "format": req.format,
        "quality": req.quality,
        "req": req,  # Store the whole request object
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
            id=job_id, user_id=user_id, url=req.url,
            format=req.format, quality=req.quality, status="queued",
        ))
        await db.commit()

    await _queue.put(job_id)
    _notify_update(job_id)
    return job_id


async def cancel_job(job_id: str, user_id: int) -> bool:
    job = _jobs.get(job_id)
    if not job or job["user_id"] != user_id:
        return False
    if job["status"] == "queued":
        job["status"] = "cancelled"
        _notify_update(job_id)
        return True
    return False


async def _process_job(job_id: str):
    job = _jobs[job_id]

    if job["status"] == "cancelled":
        return

    job["status"] = "running"
    _notify_update(job_id)

    def progress_cb(d: dict):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            job["progress"] = round((downloaded / total * 100), 1) if total else 0.0
            _notify_update(job_id)
        elif d["status"] == "finished":
            job["progress"] = 100.0
            _notify_update(job_id)

    try:
        filepath = await downloader.run_download(
            req=job["req"],
            job_id=job_id,
            user_id=job["user_id"],
            cookie_file=job["cookie_file"],
            progress_cb=progress_cb,
        )
        job["status"] = "done"
        job["filepath"] = filepath
        job["progress"] = 100.0
        _notify_update(job_id)
    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        job["status"] = "error"
        job["error_msg"] = str(exc)
        _notify_update(job_id)

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
    while True:
        job_id = await _queue.get()
        try:
            await _process_job(job_id)
        except Exception:
            logger.exception("Unhandled error in worker for job %s", job_id)
        finally:
            _queue.task_done()



async def recover_jobs():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        # Find stuck jobs
        result = await db.execute(select(models.Job).where(models.Job.status == "running"))
        stuck_jobs = result.scalars().all()
        for j in stuck_jobs:
            logger.info("Recovering stuck job %s", j.id)
            j.status = "queued"
            
            # recreate in memory
            _jobs[j.id] = {
                "id": j.id,
                "user_id": j.user_id,
                "url": j.url,
                "format": j.format,
                "quality": j.quality,
                "req": DownloadRequest(url=j.url, format=j.format, quality=j.quality), # basic rebuild
                "cookie_file": None, # might not have the original but it gets recreated on new request anyway
                "status": "queued",
                "progress": 0.0,
                "filepath": None,
                "error_msg": None,
                "title": None,
                "created_at": j.created_at.isoformat() if j.created_at else datetime.utcnow().isoformat(),
            }
            await _queue.put(j.id)
            
        await db.commit()




async def _cleanup_loop():
    while True:
        if settings.max_download_age_days > 0:
            try:
                await run_cleanup()
            except Exception as e:
                logger.exception("Error in cleanup task: %s", e)
        # Sleep for 12 hours
        await asyncio.sleep(12 * 3600)

async def run_cleanup():
    logger.info("Running cleanup task")
    from datetime import datetime, timedelta
    from sqlalchemy import select
    import shutil
    
    cutoff = datetime.utcnow() - timedelta(days=settings.max_download_age_days)
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.Job).where(models.Job.status == "done"))
        jobs = result.scalars().all()
        for j in jobs:
            if j.finished_at and j.finished_at < cutoff:
                logger.info("Expiring job %s", j.id)
                j.status = "expired"
                # Delete files
                job_dir = settings.download_root / str(j.user_id) / j.id
                if job_dir.exists():
                    shutil.rmtree(job_dir, ignore_errors=True)
        await db.commit()

async def _worker_loop():
    await recover_jobs()
    workers = []
    for _ in range(settings.worker_count):
        workers.append(asyncio.create_task(_worker()))
    workers.append(asyncio.create_task(_cleanup_loop()))
    await asyncio.gather(*workers)

def start_worker():
    global _worker_task
    _worker_task = asyncio.create_task(_worker_loop())

