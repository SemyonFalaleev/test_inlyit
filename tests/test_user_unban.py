import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import User
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_unban_user_success_as_admin(
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
            f"/user/unban/{banned_user.id}", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        print("----------------------------")
        print(response_data)
        assert response_data["is_banned"] is False

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_unban_user_as_regular_user_forbidden(
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
            banned_user = User(
                name="Banned",
                surname="User",
                email="banned@example.com",
                hashed_password="hashedpass",
                is_banned=True,
            )
            db_session.add_all([regular_user, banned_user])
            await db_session.commit()

        token = create_access_token(
            data={"sub": regular_user.email, "id": regular_user.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.patch(
            f"/user/unban/{banned_user.id}", headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_unban_user_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    try:
        async with db_session.begin():
            banned_user = User(
                name="Banned",
                surname="User",
                email="banned@example.com",
                hashed_password="hashedpass",
                is_banned=True,
            )
            db_session.add(banned_user)
            await db_session.commit()

        response = await async_client.patch(f"/user/unban/{banned_user.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_unban_user_not_found(
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

        response = await async_client.patch("/user/unban/999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "User not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_unban_already_unbanned_user(
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
            unbanned_user = User(
                name="Unbanned",
                surname="User",
                email="unbanned@example.com",
                hashed_password="hashedpass",
                is_banned=False,
            )
            db_session.add_all([admin_user, unbanned_user])
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.patch(
            f"/user/unban/{unbanned_user.id}", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["is_banned"] is False

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))
