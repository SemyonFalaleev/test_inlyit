import pytest
from httpx import AsyncClient
from main import app
from src.utils.security import create_access_token


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "test@example.com"})
    return {"Authorization": f"Bearer {token}"}
