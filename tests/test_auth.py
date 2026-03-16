import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    r = await client.post("/auth/register", json={"email": "u@x.com", "password": "pass1234"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_duplicate_register(client):
    await client.post("/auth/register", json={"email": "dup@x.com", "password": "pass1234"})
    r = await client.post("/auth/register", json={"email": "dup@x.com", "password": "pass1234"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    await client.post("/auth/register", json={"email": "cred@x.com", "password": "correct"})
    r = await client.post("/auth/login", json={"email": "cred@x.com", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_health_endpoint(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
