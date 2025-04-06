from datetime import timedelta
import pytest
from fastapi import status
from httpx import AsyncClient
from src.db.models import Advertisement
from src.db.models.category import Category
from src.db.models.complaint import Complaint
from src.db.models.review import Review
from src.db.models.user import User
from src.utils.security import create_access_token
from tests.conftest import db_session, async_client
from sqlalchemy import delete


@pytest.mark.asyncio
async def test_get_advertisement_success_with_reviews(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного получения объявления с отзывами"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Test Category")
            advertisement = Advertisement(
                name="Test Ad",
                descriptions="Test description",
                price=1000,
                user=user,
                categories=category,
            )
            review = Review(
                description="Great product!", user=user, advertisement=advertisement
            )
            db_session.add_all([user, category, advertisement, review])
            await db_session.flush()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(f"/adv/{advertisement.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == advertisement.id
        assert response_data["name"] == "Test Ad"
        assert response_data["descriptions"] == "Test description"
        assert response_data["price"] == 1000
        assert response_data["user"]["email"] == "test@example.com"
        assert response_data["category"]["name"] == "Test Category"
        assert len(response_data["reviews"]) == 1
        assert response_data["reviews"][0]["description"] == "Great product!"
    finally:
        async with db_session.begin():
            await db_session.execute(delete(Review))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_advertisement_success_without_reviews(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного получения объявления без отзывов"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test2@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Test Category")
            advertisement = Advertisement(
                name="Test Ad",
                descriptions="Test description",
                price=1000,
                user=user,
                categories=category,
            )
            db_session.add_all([user, category, advertisement])
            await db_session.flush()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(f"/adv/{advertisement.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["reviews"] == []
    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_advertisement_not_found(
    async_client: AsyncClient,
    db_session,
):
    """Тест случая, когда объявление не найдено"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test3@example.com",
                hashed_password="hashedpass",
            )
            db_session.add(user)
            await db_session.flush()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/adv/999999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Advertisemet not found"
    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_advertisement_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    """Тест случая, когда запрос без авторизации"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test4@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Test Category")
            advertisement = Advertisement(
                name="Test Ad",
                descriptions="Test description",
                user=user,
                categories=category,
            )
            db_session.add_all([user, category, advertisement])
            await db_session.flush()

        response = await async_client.get(f"/adv/{advertisement.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_advertisement_with_expired_token(
    async_client: AsyncClient,
    db_session,
):
    """Тест случая с просроченным токеном"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test6@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Test Category")
            advertisement = Advertisement(
                name="Test Ad",
                descriptions="Test description",
                user=user,
                categories=category,
            )
            db_session.add_all([user, category, advertisement])
            await db_session.flush()

        # Создаем токен с истекшим сроком действия
        token = create_access_token(
            data={"sub": user.email, "id": user.id}, expires_delta=timedelta(seconds=-1)
        )  # Отрицательное время для просрочки

        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(f"/adv/{advertisement.id}", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
