import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from src.db.models import User, Complaint, Advertisement, Category
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_get_complaints_basic(
    async_client: AsyncClient,
    db_session,
):
    """Тест базового получения списка жалоб (админ)"""
    try:
        async with db_session.begin():
            admin_user = User(
                name="Admin",
                surname="User",
                email="admin@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            regular_user = User(
                name="Regular",
                surname="User",
                email="regular@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")
            advertisement = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=regular_user,
                categories=category,
            )
            complaint1 = Complaint(
                description="Test complaint 1",
                user=regular_user,
                advertisement=advertisement,
            )
            complaint2 = Complaint(
                description="Test complaint 2",
                user=regular_user,
                advertisement=advertisement,
            )
            db_session.add_all(
                [
                    admin_user,
                    regular_user,
                    category,
                    advertisement,
                    complaint1,
                    complaint2,
                ]
            )
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(
            "/complaint/", headers=headers, params={"page": 1, "size": 10}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert all("description" in item for item in data["items"])
        assert all("user_id" in item for item in data["items"])
        assert all("adv_id" in item for item in data["items"])

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_complaints_pagination(
    async_client: AsyncClient,
    db_session,
):
    """Тест пагинации жалоб"""
    try:
        async with db_session.begin():
            admin_user = User(
                name="Admin",
                surname="User",
                email="admin@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            regular_user = User(
                name="Regular",
                surname="User",
                email="regular@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")
            advertisement = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=regular_user,
                categories=category,
            )

            complaints = []
            for i in range(15):
                complaint = Complaint(
                    description=f"Test complaint {i}",
                    user=regular_user,
                    advertisement=advertisement,
                    created_at=datetime.now() - timedelta(days=15 - i),
                )
                complaints.append(complaint)

            db_session.add_all(
                [admin_user, regular_user, category, advertisement] + complaints
            )
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(
            "/complaint/", headers=headers, params={"page": 1, "size": 5}
        )
        data = response.json()
        assert len(data["items"]) == 5
        assert data["page"] == 1
        assert data["size"] == 5
        assert data["total"] == 15

        response = await async_client.get(
            "/complaint/", headers=headers, params={"page": 2, "size": 5}
        )
        data = response.json()
        assert len(data["items"]) == 5

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_complaints_filter_by_advertisement(
    async_client: AsyncClient,
    db_session,
):
    """Тест фильтрации жалоб по объявлению"""
    try:
        async with db_session.begin():
            admin_user = User(
                name="Admin",
                surname="User",
                email="admin@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            regular_user = User(
                name="Regular",
                surname="User",
                email="regular@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")

            ad1 = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=regular_user,
                categories=category,
            )
            ad2 = Advertisement(
                name="Phone",
                descriptions="New phone",
                price=800,
                user=regular_user,
                categories=category,
            )

            complaint1 = Complaint(
                description="Complaint about laptop",
                user=regular_user,
                advertisement=ad1,
            )
            complaint2 = Complaint(
                description="Complaint about phone",
                user=regular_user,
                advertisement=ad2,
            )

            db_session.add_all(
                [admin_user, regular_user, category, ad1, ad2, complaint1, complaint2]
            )
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(
            "/complaint/", headers=headers, params={"adv_id": ad1.id}
        )
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["description"] == "Complaint about laptop"
        assert data["items"][0]["adv_id"] == ad1.id

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_complaints_sorting(
    async_client: AsyncClient,
    db_session,
):
    """Тест сортировки жалоб"""
    try:
        async with db_session.begin():
            admin_user = User(
                name="Admin",
                surname="User",
                email="admin@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            regular_user = User(
                name="Regular",
                surname="User",
                email="regular@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")
            advertisement = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=regular_user,
                categories=category,
            )

            now = datetime.now()
            complaint1 = Complaint(
                description="Old complaint",
                user=regular_user,
                advertisement=advertisement,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=1),
            )
            complaint2 = Complaint(
                description="New complaint",
                user=regular_user,
                advertisement=advertisement,
                created_at=now - timedelta(days=1),
                updated_at=now,
            )

            db_session.add_all(
                [
                    admin_user,
                    regular_user,
                    category,
                    advertisement,
                    complaint1,
                    complaint2,
                ]
            )
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(
            "/complaint/", headers=headers, params={"sort_by_create": True}
        )
        data = response.json()
        assert data["items"][0]["description"] == "New complaint"

        response = await async_client.get(
            "/complaint/", headers=headers, params={"sort_by_update": True}
        )
        data = response.json()
        assert data["items"][0]["description"] == "New complaint"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_complaints_unauthorized(
    async_client: AsyncClient,
):
    """Тест доступа без авторизации"""
    response = await async_client.get("/complaint/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_complaints_non_admin_forbidden(
    async_client: AsyncClient,
    db_session,
):
    """Тест запрета доступа для обычного пользователя"""
    try:
        async with db_session.begin():
            regular_user = User(
                name="Regular",
                surname="User",
                email="regular@example.com",
                hashed_password="hashedpass",
            )
            db_session.add(regular_user)
            await db_session.commit()

        token = create_access_token(
            data={"sub": regular_user.email, "id": regular_user.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/complaint/", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))
