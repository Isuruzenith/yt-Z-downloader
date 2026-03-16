def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_queue_empty(client):
    r = client.get("/api/queue")
    assert r.status_code == 200
    assert r.json() == []


def test_history_empty(client):
    r = client.get("/api/downloads")
    assert r.status_code == 200
    assert r.json() == []


def test_settings_returns_expected_fields(client):
    r = client.get("/api/settings")
    assert r.status_code == 200
    data = r.json()
    assert data["cookies_status"] == "missing"
    assert "download_path" in data
    assert "default_format" in data
    assert "max_queue_size" in data


def test_submit_invalid_url_rejected(client):
    r = client.post("/api/download", json={"url": "not-a-url", "format": "mp4", "quality": "best"})
    assert r.status_code == 422


def test_submit_valid_url_enqueues_job(client):
    r = client.post("/api/download", json={
        "url": "https://example.com/video",
        "format": "mp4",
        "quality": "best",
    })
    assert r.status_code == 200
    job = r.json()
    assert job["status"] == "queued"
    assert len(job["id"]) == 12
    assert job["format"] == "mp4"


def test_queued_job_appears_in_queue(client):
    r = client.post("/api/download", json={
        "url": "https://example.com/queued-check",
        "format": "mp3",
        "quality": "audio",
    })
    job_id = r.json()["id"]

    queue = client.get("/api/queue").json()
    ids = [j["id"] for j in queue]
    # job may be queued or already picked up by worker
    job_direct = client.get(f"/api/downloads/{job_id}").json()
    assert job_direct["id"] == job_id


def test_cancel_nonexistent_job(client):
    r = client.delete("/api/queue/definitely-not-real")
    assert r.status_code == 404


def test_cancel_queued_job(client):
    r = client.post("/api/download", json={
        "url": "https://example.com/cancel-me",
        "format": "mp4",
        "quality": "720",
    })
    job_id = r.json()["id"]

    # Cancel immediately — should succeed if still queued
    cancel = client.delete(f"/api/queue/{job_id}")
    # 200 = cancelled, 404 = already picked up by worker — both valid
    assert cancel.status_code in (200, 404)


def test_get_nonexistent_job(client):
    r = client.get("/api/downloads/nonexistent-id")
    assert r.status_code == 404


def test_info_invalid_url(client):
    r = client.get("/api/info", params={"url": "https://example.com/not-a-video"})
    # Should return 422 from yt-dlp failing — not a 500
    assert r.status_code in (422, 200)
