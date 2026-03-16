import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_enqueue_job(client, auth_headers):
    with patch("api.downloader.run_download", new_callable=AsyncMock) as mock_dl:
        mock_dl.return_value = "/downloads/1/job1/video.mp4"
        r = await client.post(
            "/api/download",
            json={"url": "https://youtube.com/watch?v=test", "format": "mp4", "quality": "720p"},
            headers=auth_headers,
        )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("queued", "running", "done")
    assert data["url"] == "https://youtube.com/watch?v=test"
    assert data["format"] == "mp4"
    assert data["quality"] == "720p"


@pytest.mark.asyncio
async def test_get_queue(client, auth_headers):
    r = await client.get("/api/queue", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_cancel_nonexistent_job(client, auth_headers):
    r = await client.delete("/api/queue/nonexistent-id", headers=auth_headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_download_requires_auth(client):
    r = await client.post(
        "/api/download",
        json={"url": "https://youtube.com/watch?v=test"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_history_endpoint(client, auth_headers):
    r = await client.get("/api/downloads", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
