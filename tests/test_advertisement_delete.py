import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import Advertisement, Category, User
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_delete_advertisement_success(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного удаления объявления владельцем"""
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
            db_session.add_all([user, category, advertisement])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.delete(
            f"/adv/{advertisement.id}", headers=headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        async with db_session.begin():
            result = await db_session.execute(
                select(Advertisement).where(Advertisement.id == advertisement.id)
            )
            assert result.scalar_one_or_none() is None

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_delete_advertisement_admin_success(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного удаления объявления администратором"""
    try:
        async with db_session.begin():
            owner = User(
                name="Owner",
                surname="User",
                email="owner@example.com",
                hashed_password="hashedpass",
            )
            admin = User(
                name="Admin",
                surname="User",
                email="admin@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            category = Category(name="Test Category")
            advertisement = Advertisement(
                name="Test Ad",
                descriptions="Test description",
                price=1000,
                user=owner,
                categories=category,
            )
            db_session.add_all([owner, admin, category, advertisement])
            await db_session.commit()

        token = create_access_token(data={"sub": admin.email, "id": admin.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.delete(
            f"/adv/{advertisement.id}", headers=headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        async with db_session.begin():
            result = await db_session.execute(
                select(Advertisement).where(Advertisement.id == advertisement.id)
            )
            assert result.scalar_one_or_none() is None

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_delete_advertisement_not_found(
    async_client: AsyncClient,
    db_session,
):
    """Тест удаления несуществующего объявления"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test2@example.com",
                hashed_password="hashedpass",
            )
            db_session.add(user)
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.delete("/adv/999999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Advertisement not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_delete_advertisement_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    """Тест удаления без авторизации"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test3@example.com",
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
            await db_session.commit()

        response = await async_client.delete(f"/adv/{advertisement.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_delete_advertisement_not_owner(
    async_client: AsyncClient,
    db_session,
):
    """Тест удаления чужого объявления"""
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
            category = Category(name="Test Category")
            advertisement = Advertisement(
                name="Test Ad",
                descriptions="Test description",
                price=1000,
                user=owner,
                categories=category,
            )
            db_session.add_all([owner, other_user, category, advertisement])
            await db_session.commit()

        token = create_access_token(data={"sub": other_user.email, "id": other_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.delete(
            f"/adv/{advertisement.id}", headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
