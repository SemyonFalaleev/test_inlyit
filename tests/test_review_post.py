import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from datetime import datetime
from src.db.models import User, Review, Advertisement, Category
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_create_review_success(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного создания отзыва"""
    try:
        async with db_session.begin():
            owner = User(
                name="Owner",
                surname="User",
                email="owner@example.com",
                hashed_password="hashedpass",
            )
            reviewer = User(
                name="Reviewer",
                surname="User",
                email="reviewer@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")
            advertisement = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=owner,
                categories=category,
            )
            db_session.add_all([owner, reviewer, category, advertisement])
            await db_session.commit()

        token = create_access_token(data={"sub": reviewer.email, "id": reviewer.id})
        headers = {"Authorization": f"Bearer {token}"}

        review_data = {
            "description": "Great product!",
        }

        response = await async_client.post(
            f"/review/{advertisement.id}", json=review_data, headers=headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["description"] == "Great product!"
        assert data["user_id"] == reviewer.id
        assert data["adv_id"] == advertisement.id

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Review))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_create_review_relationships(
    async_client: AsyncClient,
    db_session,
):
    """Тест корректности связей при создании отзыва"""
    try:
        async with db_session.begin():
            owner = User(
                name="Owner",
                surname="User",
                email="owner@example.com",
                hashed_password="hashedpass",
            )
            reviewer = User(
                name="Reviewer",
                surname="User",
                email="reviewer@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")
            advertisement = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=owner,
                categories=category,
            )
            db_session.add_all([owner, reviewer, category, advertisement])
            await db_session.commit()

        token = create_access_token(data={"sub": reviewer.email, "id": reviewer.id})
        headers = {"Authorization": f"Bearer {token}"}

        review_data = {
            "description": "Testing relationships",
        }

        response = await async_client.post(
            f"/review/{advertisement.id}", json=review_data, headers=headers
        )

        assert response.status_code == status.HTTP_201_CREATED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Review))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
