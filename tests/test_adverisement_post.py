import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import Advertisement, Category, User
from src.utils.security import create_access_token
from src.dto.adv_dto import AdvertisementCreateDTO
import json


@pytest.mark.asyncio
async def test_create_advertisement_success(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного создания объявления"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Test Category")
            db_session.add_all([user, category])
            await db_session.flush()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        adv_data = {
            "name": "New Advertisement",
            "descriptions": "Test description",
            "price": 1000,
            "category_id": category.id,
        }

        response = await async_client.post("/adv/", json=adv_data, headers=headers)

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == "New Advertisement"
        assert response_data["user"]["email"] == "test@example.com"
        assert response_data["category"]["name"] == "Test Category"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_create_advertisement_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    """Тест создания объявления без авторизации"""
    try:
        async with db_session.begin():
            category = Category(name="Test Category")
            db_session.add(category)
            await db_session.flush()

        adv_data = {
            "name": "New Advertisement",
            "descriptions": "Test description",
            "price": 1000,
            "category_id": category.id,
        }

        response = await async_client.post("/adv/", json=adv_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))


@pytest.mark.asyncio
async def test_create_advertisement_invalid_category(
    async_client: AsyncClient,
    db_session,
):
    """Тест создания объявления с несуществующей категорией"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test2@example.com",
                hashed_password="hashedpass",
            )
            db_session.add(user)
            await db_session.flush()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        adv_data = {
            "name": "New Advertisement",
            "descriptions": "Test description",
            "price": 1000,
            "category_id": 99999,
        }

        response = await async_client.post("/adv/", json=adv_data, headers=headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Category not found" in response.json().get("detail", "")

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_create_advertisement_missing_required_field(
    async_client: AsyncClient,
    db_session,
):
    """Тест создания объявления без обязательного поля"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test3@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Test Category")
            db_session.add_all([user, category])
            await db_session.flush()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        adv_data = {
            "descriptions": "Test description",
            "price": 1000,
            "category_id": category.id,
        }

        response = await async_client.post("/adv/", json=adv_data, headers=headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
