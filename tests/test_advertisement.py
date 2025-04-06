from fastapi.testclient import TestClient
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from src.db.models import User, Category
from main import app
from tests.conftest import async_client, auth_headers

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_advertisement_success(
    async_client: AsyncClient, db_session: AsyncSession, auth_headers: dict
):
    # Setup test data
    test_user = User(
        id=1,
        name="Test",
        surname="User",
        email="test@example.com",
        hashed_password="hashedpass",
        is_admin=False,
        is_banned=False,
    )

    test_category = Category(id=1, name="Test Category")

    db_session.add(test_user)
    db_session.add(test_category)
    await db_session.commit()

    # Mock dependencies
    with patch("src.utils.security.get_current_user", return_value=test_user):
        # Test request
        adv_data = {
            "name": "Test Ad",
            "descriptions": "Test description",
            "price": 100,
            "category_id": 1,
        }

        response = await async_client.post(
            "/advertisements/", json=adv_data, headers=auth_headers
        )

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    assert response_data["name"] == adv_data["name"]
    assert response_data["descriptions"] == adv_data["descriptions"]
    assert response_data["price"] == adv_data["price"]
    assert response_data["user"]["id"] == test_user.id
    assert response_data["category"]["id"] == test_category.id


@pytest.mark.asyncio
async def test_create_advertisement_unauthorized(async_client: AsyncClient):
    # Test request without auth
    adv_data = {
        "name": "Test Ad",
        "descriptions": "Test description",
        "price": 100,
        "category_id": 1,
    }

    response = await async_client.post("/advertisements/", json=adv_data)

    # Assertions
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_advertisement_invalid_category(
    async_client: AsyncClient, auth_headers: dict, db_session: AsyncSession
):
    # Setup test user
    test_user = User(
        id=1,
        name="Test",
        surname="User",
        email="test@example.com",
        hashed_password="hashedpass",
        is_admin=False,
        is_banned=False,
    )

    db_session.add(test_user)
    await db_session.commit()

    # Mock dependencies
    with patch("src.utils.security.get_current_user", return_value=test_user):
        # Test request with invalid category
        adv_data = {
            "name": "Test Ad",
            "descriptions": "Test description",
            "price": 100,
            "category_id": 999,  # non-existent category
        }

        response = await async_client.post(
            "/advertisements/", json=adv_data, headers=auth_headers
        )

    # Assertions
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Foreign key violation" in response.text


@pytest.mark.asyncio
async def test_create_advertisement_missing_required_fields(
    async_client: AsyncClient, auth_headers: dict
):
    # Test request with missing required field
    adv_data = {"descriptions": "Test description", "price": 100, "category_id": 1}

    response = await async_client.post(
        "/advertisements/", json=adv_data, headers=auth_headers
    )

    # Assertions
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "name" in response.text


@pytest.mark.asyncio
async def test_create_advertisement_db_error(
    async_client: AsyncClient, auth_headers: dict, db_session: AsyncSession
):
    # Setup test data
    test_user = User(
        id=1,
        name="Test",
        surname="User",
        email="test@example.com",
        hashed_password="hashedpass",
        is_admin=False,
        is_banned=False,
    )

    test_category = Category(id=1, name="Test Category")

    db_session.add(test_user)
    db_session.add(test_category)
    await db_session.commit()

    # Mock dependencies and force DB error
    with patch(
        "src.utils.security.get_current_user", return_value=test_user
    ), patch.object(db_session, "commit", side_effect=Exception("DB error")):

        adv_data = {
            "name": "Test Ad",
            "descriptions": "Test description",
            "price": 100,
            "category_id": 1,
        }

        response = await async_client.post(
            "/advertisements/", json=adv_data, headers=auth_headers
        )

    # Assertions
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "DB error" in response.text


@pytest.mark.asyncio
async def test_create_advertisement_model_validation(
    async_client: AsyncClient, auth_headers: dict
):
    # Test request with invalid data
    adv_data = {
        "name": "T" * 151,  # exceeds max length
        "descriptions": "Test description",
        "price": 100,
        "category_id": 1,
    }

    response = await async_client.post(
        "/advertisements/", json=adv_data, headers=auth_headers
    )

    # Assertions
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "ensure this value has at most 150 characters" in response.text
