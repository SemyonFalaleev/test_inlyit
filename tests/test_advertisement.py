import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import Advertisement, Category, User
from src.utils.security import create_access_token
from src.dto.adv_dto import AdvertisementUpdateDTO
import json
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete
from src.db.models import Advertisement, Category, User
from src.utils.security import create_access_token
import json


@pytest.mark.asyncio
async def test_patch_advertisement_success(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного обновления объявления владельцем"""
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
                name="Old Name",
                descriptions="Old Description",
                price=1000,
                user=user,
                categories=category,
            )
            db_session.add_all([user, category, advertisement])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {
            "name": "New Name",
            "descriptions": "New Description",
            "price": 2000,
        }

        response = await async_client.patch(
            f"/adv/{advertisement.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "New Name"
        assert response_data["descriptions"] == "New Description"
        assert response_data["price"] == 2000

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_patch_advertisement_admin_success(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного обновления объявления администратором"""
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
                descriptions="Test Description",
                price=1000,
                user=owner,
                categories=category,
            )
            db_session.add_all([owner, admin, category, advertisement])
            await db_session.commit()

        token = create_access_token(data={"sub": admin.email, "id": admin.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"name": "Admin Updated Name"}

        response = await async_client.patch(
            f"/adv/{advertisement.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "Admin Updated Name"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_patch_advertisement_change_category(
    async_client: AsyncClient,
    db_session,
):
    """Тест успешного обновления категории объявления"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test2@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Old Category")
            new_category = Category(name="New Category")
            advertisement = Advertisement(
                name="Test Ad",
                descriptions="Test Description",
                price=1000,
                user=user,
                categories=category,
            )
            db_session.add_all([user, category, new_category, advertisement])
            await db_session.flush()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.patch(
            f"/adv/{advertisement.id}?cat_id={new_category.id}",
            json={},
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["category"]["name"] == "New Category"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_patch_advertisement_unauthorized(
    async_client: AsyncClient,
    db_session,
):
    """Тест обновления объявления без авторизации"""
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
                descriptions="Test Description",
                price=1000,
                user=user,
                categories=category,
            )
            db_session.add_all([user, category, advertisement])
            await db_session.flush()

        update_data = {"name": "New Name"}

        response = await async_client.patch(
            f"/adv/{advertisement.id}", json=update_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_patch_advertisement_not_owner(
    async_client: AsyncClient,
    db_session,
):
    """Тест обновления чужого объявления"""
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
                descriptions="Test Description",
                price=1000,
                user=owner,
                categories=category,
            )
            db_session.add_all([owner, other_user, category, advertisement])
            await db_session.flush()

        token = create_access_token(data={"sub": other_user.email, "id": other_user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"name": "Hacked Name"}

        response = await async_client.patch(
            f"/adv/{advertisement.id}", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_patch_advertisement_not_found(
    async_client: AsyncClient,
    db_session,
):
    """Тест обновления несуществующего объявления"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test4@example.com",
                hashed_password="hashedpass",
            )
            db_session.add(user)
            await db_session.flush()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"name": "New Name"}

        response = await async_client.patch(
            "/adv/999999", json=update_data, headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Advertisement not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_patch_advertisement_invalid_category(
    async_client: AsyncClient,
    db_session,
):
    """Тест обновления с несуществующей категорией"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test5@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Test Category")
            advertisement = Advertisement(
                name="Test Ad",
                descriptions="Test Description",
                price=1000,
                user=user,
                categories=category,
            )
            db_session.add_all([user, category, advertisement])
            await db_session.flush()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.patch(
            f"/adv/{advertisement.id}?cat_id=999999", json={}, headers=headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Category not found"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))
