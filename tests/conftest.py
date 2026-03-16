import os
import tempfile

import pytest

# Must be set before any api imports so pydantic-settings reads them
_tmp = tempfile.mkdtemp()
os.environ["DATA_PATH"] = _tmp
os.environ["COOKIES_PATH"] = _tmp
os.environ["DOWNLOAD_PATH"] = _tmp
os.environ["API_KEY"] = ""  # disable auth

from fastapi.testclient import TestClient  # noqa: E402
from api.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
