import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete
from src.db.models import User, Review, Advertisement, Category
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_get_review_success(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного получения отзыва"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")
            advertisement = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=user,
                categories=category,
            )
            review = Review(
                description="Test review", user=user, advertisement=advertisement
            )
            db_session.add_all([user, category, advertisement, review])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(f"/review/{review.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == review.id
        assert data["description"] == "Test review"
        assert data["user_id"] == user.id
        assert data["adv_id"] == advertisement.id

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Review))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_review_not_found(
    async_client: AsyncClient,
    db_session,
):
    """Тест получения несуществующего отзыва"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test@example.com",
                hashed_password="hashedpass",
            )
            db_session.add(user)
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(f"/review/999999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Review not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


async def test_get_review_relationships(
    async_client: AsyncClient,
    db_session,
):
    """Тест корректности связей в возвращаемых данных"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")
            advertisement = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=user,
                categories=category,
            )
            review = Review(
                description="Test review with relationships",
                user=user,
                advertisement=advertisement,
            )
            db_session.add_all([user, category, advertisement, review])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(f"/review/{review.id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == user.id
        assert data["adv_id"] == advertisement.id

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Review))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
