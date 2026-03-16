from __future__ import annotations

import asyncio
import datetime
import uuid
from typing import Optional

from .models import DownloadJob, DownloadRequest, Format, Quality, Status
from . import downloader as dl
from .history import HistoryStore


class JobQueue:
    def __init__(self, history: HistoryStore) -> None:
        self._jobs: dict[str, DownloadJob] = {}
        self._queue: asyncio.Queue[str]     # created in start() inside the running loop
        self._history = history
        self._worker_task: Optional[asyncio.Task] = None

    def start(self) -> None:
        # Create the queue here so it binds to the current event loop
        self._jobs = {}
        self._queue = asyncio.Queue()
        self._worker_task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    def all_jobs(self) -> list[DownloadJob]:
        return list(self._jobs.values())

    def get_job(self, job_id: str) -> Optional[DownloadJob]:
        return self._jobs.get(job_id)

    async def enqueue(self, req: DownloadRequest) -> DownloadJob:
        job = DownloadJob(
            id=uuid.uuid4().hex[:12],
            url=req.url,
            format=req.format,
            quality=req.quality,
            status=Status.queued,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self._jobs[job.id] = job
        await self._queue.put(job.id)
        return job

    def cancel(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job and job.status == Status.queued:
            job.status = Status.cancelled
            return True
        return False

    async def _worker(self) -> None:
        while True:
            job_id = await self._queue.get()
            job = self._jobs.get(job_id)

            if job is None or job.status == Status.cancelled:
                self._queue.task_done()
                continue

            job.status = Status.running

            def on_progress(pct: float, size_mb: float | None) -> None:
                job.progress = pct
                if size_mb is not None:
                    job.size_mb = size_mb

            try:
                title, path = await dl.download(
                    url=job.url,
                    fmt=job.format,
                    quality=job.quality,
                    on_progress=on_progress,
                )
                job.title = title
                job.path = path
                job.status = Status.done
                job.progress = 100.0
                job.completed_at = datetime.datetime.now(datetime.timezone.utc)
                await self._history.append(job)
            except Exception as exc:
                job.status = Status.failed
                job.error = str(exc)
            finally:
                self._queue.task_done()
