import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import Category, User
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_get_category_success_as_admin(
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
            test_category = Category(name="Electronics")
            db_session.add_all([admin_user, test_category])
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(
            f"/category/{test_category.id}", headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == test_category.id
        assert response_data["name"] == "Electronics"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_category_as_regular_user_forbidden(
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
            test_category = Category(name="Electronics")
            db_session.add_all([regular_user, test_category])
            await db_session.commit()

        token = create_access_token(
            data={"sub": regular_user.email, "id": regular_user.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(
            f"/category/{test_category.id}", headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_category_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    try:
        async with db_session.begin():
            test_category = Category(name="Electronics")
            db_session.add(test_category)
            await db_session.commit()

        response = await async_client.get(f"/category/{test_category.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))


@pytest.mark.asyncio
async def test_get_category_not_found(
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

        response = await async_client.get("/category/999", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Category not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))
