import os
import asyncio
import tempfile

# Must be set before any api modules are imported so settings picks up the temp path
_tmp_data = tempfile.mkdtemp()
os.environ.setdefault("DATA_ROOT", _tmp_data)

import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app
from api.db import engine, Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_headers(client):
    await client.post("/auth/register", json={"email": "test@example.com", "password": "testpass123"})
    res = await client.post("/auth/login", json={"email": "test@example.com", "password": "testpass123"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
