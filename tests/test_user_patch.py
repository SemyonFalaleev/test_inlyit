import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import User
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_update_user_success_as_admin(
    async_client: AsyncClient,
    db_session,
):
    try:
        async with db_session.begin():
            admin_user = User(
                name="Admin",
                surname="User",
                email="admin@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            test_user = User(
                name="Test",
                surname="User",
                email="test@example.com",
                hashed_password="hashedpass",
            )
            db_session.add_all([admin_user, test_user])
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {
            "name": "Updated",
            "surname": "Name",
            "email": "updated@example.com",
        }

        response = await async_client.patch(
            f"/user/{test_user.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "Updated"
        assert response_data["surname"] == "Name"
        assert response_data["email"] == "updated@example.com"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_user_as_regular_user_forbidden(
    async_client: AsyncClient,
    db_session,
):
    try:
        async with db_session.begin():
            regular_user1 = User(
                name="Regular1",
                surname="User",
                email="regular1@example.com",
                hashed_password="hashedpass",
            )
            regular_user2 = User(
                name="Regular2",
                surname="User",
                email="regular2@example.com",
                hashed_password="hashedpass",
            )
            db_session.add_all([regular_user1, regular_user2])
            await db_session.commit()

        token = create_access_token(
            data={"sub": regular_user1.email, "id": regular_user1.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"name": "Updated"}

        response = await async_client.patch(
            f"/user/{regular_user2.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_user_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    try:
        async with db_session.begin():
            test_user = User(
                name="Test",
                surname="User",
                email="test@example.com",
                hashed_password="hashedpass",
            )
            db_session.add(test_user)
            await db_session.commit()

        update_data = {"name": "Updated"}

        response = await async_client.patch(f"/user/{test_user.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_user_not_found(
    async_client: AsyncClient,
    db_session,
):
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

        update_data = {"name": "Updated"}

        response = await async_client.patch(
            "/user/999", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "User not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_update_user_email_conflict(
    async_client: AsyncClient,
    db_session,
):
    try:
        async with db_session.begin():
            admin_user = User(
                name="Admin",
                surname="User",
                email="admin@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            test_user1 = User(
                name="Test1",
                surname="User",
                email="test1@example.com",
                hashed_password="hashedpass",
            )
            test_user2 = User(
                name="Test2",
                surname="User",
                email="test2@example.com",
                hashed_password="hashedpass",
            )
            db_session.add_all([admin_user, test_user1, test_user2])
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"email": "test2@example.com"}

        response = await async_client.patch(
            f"/user/{test_user1.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))
