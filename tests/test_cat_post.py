import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import Category, User
from src.utils.security import create_access_token


@pytest.mark.asyncio
async def test_create_category_success_as_admin(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного создания категории администратором"""
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

        category_data = {"name": "Electronics"}

        response = await async_client.post(
            "/category/", json=category_data, headers=headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == "Electronics"

        async with db_session.begin():
            result = await db_session.execute(
                select(Category).where(Category.name == "Electronics")
            )
            category = result.scalar_one_or_none()
            assert category is not None

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_create_category_as_regular_user(
    async_client: AsyncClient,
    db_session,
):
    """Тест попытки создания категории обычным пользователем"""
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

        token = create_access_token(
            data={"sub": regular_user.email, "id": regular_user.id}
        )
        headers = {"Authorization": f"Bearer {token}"}

        category_data = {"name": "Electronics"}

        response = await async_client.post(
            "/category/", json=category_data, headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_create_category_unauthorized(
    async_client: AsyncClient,
):
    """Тест создания категории без авторизации"""
    category_data = {"name": "Electronics"}

    response = await async_client.post("/category/", json=category_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_category_duplicate_name_as_admin(
    async_client: AsyncClient,
    db_session,
):
    """Тест создания дубликата категории администратором"""
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

        category_data = {"name": "Electronics"}

        response = await async_client.post(
            "/category/", json=category_data, headers=headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "A category with this name already exists"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
