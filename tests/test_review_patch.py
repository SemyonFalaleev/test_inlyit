import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import delete
from src.db.models import User, Review, Advertisement, Category
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_update_review_success_as_owner(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного обновления отзыва владельцем"""
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
                description="Initial review", user=user, advertisement=advertisement
            )
            db_session.add_all([user, category, advertisement, review])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"description": "Updated review text"}

        response = await async_client.patch(
            f"/review/{review.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated review text"
        assert data["id"] == review.id

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Review))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_review_success_as_admin(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного обновления отзыва администратором"""
    try:
        async with db_session.begin():
            admin = User(
                name="Admin",
                surname="User",
                email="admin@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
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
                description="Initial review", user=user, advertisement=advertisement
            )
            db_session.add_all([admin, user, category, advertisement, review])
            await db_session.commit()

        token = create_access_token(data={"sub": admin.email, "id": admin.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"description": "Admin updated this review"}

        response = await async_client.patch(
            f"/review/{review.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Admin updated this review"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Review))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_review_as_other_user_forbidden(
    async_client: AsyncClient,
    db_session,
):
    """Тест запрета обновления чужого отзыва"""
    try:
        async with db_session.begin():
            owner = User(
                name="Owner",
                surname="User",
                email="owner@example.com",
                hashed_password="hashedpass",
            )
            other_user = User(
                name="Other",
                surname="User",
                email="other@example.com",
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
            review = Review(
                description="Initial review", user=owner, advertisement=advertisement
            )
            db_session.add_all([owner, other_user, category, advertisement, review])
            await db_session.commit()

        token = create_access_token(data={"sub": other_user.email, "id": other_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"description": "Unauthorized update"}

        response = await async_client.patch(
            f"/review/{review.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Review))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_review_not_found(
    async_client: AsyncClient,
    db_session,
):
    """Тест обновления несуществующего отзыва"""
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

        update_data = {"description": "No such review"}

        response = await async_client.patch(
            "/review/999", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Review not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))
