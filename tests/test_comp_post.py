import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import User, Complaint, Advertisement, Category
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_create_complaint_success(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного создания жалобы на объявление"""
    try:
        async with db_session.begin():
            owner = User(
                name="Owner",
                surname="User",
                email="owner@example.com",
                hashed_password="hashedpass",
            )

            complainant = User(
                name="Complainant",
                surname="User",
                email="complainant@example.com",
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
            db_session.add_all([owner, complainant, category, advertisement])
            await db_session.commit()

        token = create_access_token(
            data={"sub": complainant.email, "id": complainant.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        complaint_data = {"description": "This ad is suspicious"}

        response = await async_client.post(
            f"/complaint/{advertisement.id}", json=complaint_data, headers=headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["description"] == "This ad is suspicious"
        assert data["user_id"] == complainant.id
        assert data["adv_id"] == advertisement.id

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_create_complaint_for_own_ad(
    async_client: AsyncClient,
    db_session,
):
    """Тест попытки создать жалобу на свое собственное объявление"""
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
            db_session.add_all([user, category, advertisement])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        complaint_data = {"description": "This is my own ad"}

        response = await async_client.post(
            f"/complaint/{advertisement.id}", json=complaint_data, headers=headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_create_complaint_ad_not_found(
    async_client: AsyncClient,
    db_session,
):
    """Тест создания жалобы на несуществующее объявление"""
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

        complaint_data = {"description": "This ad doesn't exist"}

        response = await async_client.post(
            "/complaint/999", json=complaint_data, headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Advertisement not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_create_complaint_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    """Тест создания жалобы без авторизации"""
    try:
        async with db_session.begin():
            owner = User(
                name="Owner",
                surname="User",
                email="owner@example.com",
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
            db_session.add_all([owner, category, advertisement])
            await db_session.commit()

        complaint_data = {"description": "Unauthorized complaint"}

        response = await async_client.post(
            f"/complaint/{advertisement.id}", json=complaint_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_create_complaint_missing_description(
    async_client: AsyncClient,
    db_session,
):
    """Тест создания жалобы без описания"""
    try:
        async with db_session.begin():
            owner = User(
                name="Owner",
                surname="User",
                email="owner@example.com",
                hashed_password="hashedpass",
            )
            complainant = User(
                name="Complainant",
                surname="User",
                email="complainant@example.com",
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
            db_session.add_all([owner, complainant, category, advertisement])
            await db_session.commit()

        token = create_access_token(
            data={"sub": complainant.email, "id": complainant.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        complaint_data = {}

        response = await async_client.post(
            f"/complaint/{advertisement.id}", json=complaint_data, headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
