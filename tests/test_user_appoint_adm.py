import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import User
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_appoint_admin_success_as_admin(
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
            regular_user = User(
                name="Regular",
                surname="User",
                email="regular@example.com",
                hashed_password="hashedpass",
                is_admin=False,
            )
            db_session.add_all([admin_user, regular_user])
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.patch(
            f"/user/adm/{regular_user.id}", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["is_admin"] is True

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_appoint_admin_as_regular_user_forbidden(
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
                is_admin=False,
            )
            regular_user2 = User(
                name="Regular2",
                surname="User",
                email="regular2@example.com",
                hashed_password="hashedpass",
                is_admin=False,
            )
            db_session.add_all([regular_user1, regular_user2])
            await db_session.commit()

        token = create_access_token(
            data={"sub": regular_user1.email, "id": regular_user1.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.patch(
            f"/user/adm/{regular_user2.id}", headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_appoint_admin_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    try:
        async with db_session.begin():
            regular_user = User(
                name="Regular",
                surname="User",
                email="regular@example.com",
                hashed_password="hashedpass",
                is_admin=False,
            )
            db_session.add(regular_user)
            await db_session.commit()

        response = await async_client.patch(f"/user/adm/{regular_user.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_appoint_admin_not_found(
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

        response = await async_client.patch("/user/adm/999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "User not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_appoint_admin_to_banned_user(
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
            banned_user = User(
                name="Banned",
                surname="User",
                email="banned@example.com",
                hashed_password="hashedpass",
                is_banned=True,
            )
            db_session.add_all([admin_user, banned_user])
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.patch(
            f"/user/adm/{banned_user.id}", headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "User is banned" in response.json()["detail"]

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_appoint_admin_to_already_admin(
    async_client: AsyncClient,
    db_session,
):
    try:
        async with db_session.begin():
            admin_user1 = User(
                name="Admin1",
                surname="User",
                email="admin1@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            admin_user2 = User(
                name="Admin2",
                surname="User",
                email="admin2@example.com",
                hashed_password="hashedpass",
                is_admin=True,
            )
            db_session.add_all([admin_user1, admin_user2])
            await db_session.commit()

        token = create_access_token(
            data={"sub": admin_user1.email, "id": admin_user1.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.patch(
            f"/user/adm/{admin_user2.id}", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["is_admin"] is True

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))
