import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import Category, User
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_patch_category_success_as_admin(
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
            existing_category = Category(name="Electronics")
            db_session.add_all([admin_user, existing_category])
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"name": "Updated Electronics"}

        response = await async_client.patch(
            f"/category/{existing_category.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "Updated Electronics"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_patch_category_as_regular_user(
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
            existing_category = Category(name="Electronics")
            db_session.add_all([regular_user, existing_category])
            await db_session.commit()

        token = create_access_token(
            data={"sub": regular_user.email, "id": regular_user.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"name": "Updated Electronics"}

        response = await async_client.patch(
            f"/category/{existing_category.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_patch_category_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    try:
        async with db_session.begin():
            existing_category = Category(name="Electronics")
            db_session.add(existing_category)
            await db_session.commit()

        update_data = {"name": "Updated Electronics"}

        response = await async_client.patch(
            f"/category/{existing_category.id}", json=update_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))


@pytest.mark.asyncio
async def test_patch_category_not_found(
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

        update_data = {"name": "Updated Electronics"}

        response = await async_client.patch(
            "/category/999", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Category not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_patch_category_duplicate_name(
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
            existing_category1 = Category(name="Electronics")
            existing_category2 = Category(name="Clothing")
            db_session.add_all([admin_user, existing_category1, existing_category2])
            await db_session.commit()

        token = create_access_token(data={"sub": admin_user.email, "id": admin_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"name": "Clothing"}

        response = await async_client.patch(
            f"/category/{existing_category1.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
