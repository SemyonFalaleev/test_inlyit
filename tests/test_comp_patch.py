import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from datetime import datetime
from src.db.models import User, Complaint, Advertisement, Category
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_update_complaint_success_as_admin(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного обновления жалобы администратором"""
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
            complaint = Complaint(
                description="Old description",
                user=regular_user,
                advertisement=advertisement,
            )
            db_session.add_all(
                [admin_user, regular_user, category, advertisement, complaint]
            )
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"description": "Updated description"}

        response = await async_client.patch(
            f"/complaint/{complaint.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_complaint_success_as_owner(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного обновления жалобы владельцем"""
    try:
        async with db_session.begin():
            test_user = User(
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
                user=test_user,
                categories=category,
            )
            complaint = Complaint(
                description="Old description",
                user=test_user,
                advertisement=advertisement,
            )
            db_session.add_all([test_user, category, advertisement, complaint])
            await db_session.commit()

        token = create_access_token(data={"sub": test_user.email, "id": test_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"description": "Updated by owner"}

        response = await async_client.patch(
            f"/complaint/{complaint.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated by owner"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_complaint_as_other_user_forbidden(
    async_client: AsyncClient,
    db_session,
):
    """Тест запрета обновления чужой жалобы"""
    try:
        async with db_session.begin():
            user1 = User(
                name="User1",
                surname="User",
                email="user1@example.com",
                hashed_password="hashedpass",
            )
            user2 = User(
                name="User2",
                surname="User",
                email="user2@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")
            advertisement = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=user1,
                categories=category,
            )
            complaint = Complaint(
                description="Test complaint", user=user1, advertisement=advertisement
            )
            db_session.add_all([user1, user2, category, advertisement, complaint])
            await db_session.commit()

        token = create_access_token(data={"sub": user2.email, "id": user2.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"description": "Unauthorized update"}

        response = await async_client.patch(
            f"/complaint/{complaint.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_complaint_not_found(
    async_client: AsyncClient,
    db_session,
):
    """Тест обновления несуществующей жалобы"""
    try:
        async with db_session.begin():
            admin_user = User(
                name="Admin",
                surname="User",
                email="admin@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            db_session.add(admin_user)
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"description": "New description"}

        response = await async_client.patch(
            "/complaint/999", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Complaint not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_complaint_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    """Тест обновления жалобы без авторизации"""
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
            complaint = Complaint(
                description="Test complaint", user=user, advertisement=advertisement
            )
            db_session.add_all([user, category, advertisement, complaint])
            await db_session.commit()

        update_data = {"description": "Unauthorized update"}

        response = await async_client.patch(
            f"/complaint/{complaint.id}", json=update_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_complaint_partial_data(
    async_client: AsyncClient,
    db_session,
):
    """Тест частичного обновления жалобы"""
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
            complaint = Complaint(
                description="Original description",
                user=regular_user,
                advertisement=advertisement,
            )
            db_session.add_all(
                [admin_user, regular_user, category, advertisement, complaint]
            )
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"description": "Updated description"}

        response = await async_client.patch(
            f"/complaint/{complaint.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["user_id"] == regular_user.id
        assert data["adv_id"] == advertisement.id

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Complaint))
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
