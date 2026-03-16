import asyncio
import os

from api.models import DownloadRequest, Format, Quality, Status


def _make_queue(tmp_path):
    os.environ["DATA_PATH"] = str(tmp_path)
    from api.history import HistoryStore
    from api.queue import JobQueue
    return JobQueue(HistoryStore())


async def _started(q):
    """Start the queue inside a running event loop so asyncio.Queue binds correctly."""
    q.start()
    return q


def test_enqueue_creates_queued_job(tmp_path):
    async def run():
        q = await _started(_make_queue(tmp_path))
        req = DownloadRequest(url="https://example.com", format=Format.mp4, quality=Quality.best)
        job = await q.enqueue(req)
        assert job.status == Status.queued
        assert job.id in {j.id for j in q.all_jobs()}
        assert job.url == "https://example.com"
        await q.stop()

    asyncio.run(run())


def test_enqueue_multiple_jobs(tmp_path):
    async def run():
        q = await _started(_make_queue(tmp_path))
        req = DownloadRequest(url="https://example.com", format=Format.mp4, quality=Quality.best)
        job1 = await q.enqueue(req)
        job2 = await q.enqueue(req)
        assert job1.id != job2.id
        assert len(q.all_jobs()) == 2
        await q.stop()

    asyncio.run(run())


def test_cancel_queued_job(tmp_path):
    async def run():
        q = await _started(_make_queue(tmp_path))
        req = DownloadRequest(url="https://example.com", format=Format.mp4, quality=Quality.best)
        job = await q.enqueue(req)
        result = q.cancel(job.id)
        assert result is True
        assert q.get_job(job.id).status == Status.cancelled
        await q.stop()

    asyncio.run(run())


def test_cancel_nonexistent_returns_false(tmp_path):
    q = _make_queue(tmp_path)
    assert q.cancel("no-such-id") is False


def test_get_job_returns_none_for_unknown(tmp_path):
    q = _make_queue(tmp_path)
    assert q.get_job("unknown") is None


def test_all_jobs_empty_on_init(tmp_path):
    q = _make_queue(tmp_path)
    assert q.all_jobs() == []
