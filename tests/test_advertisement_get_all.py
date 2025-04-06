import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select, delete, func
from src.db.models import Advertisement, Category, User
from src.utils.security import create_access_token
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_get_advertisements_basic(
    async_client: AsyncClient,
    db_session,
):
    """Тест базового получения списка объявлений"""
    try:
        async with db_session.begin():
            user = User(
                name="Test",
                surname="User",
                email="test@example.com",
                hashed_password="hashedpass",
            )
            category = Category(name="Electronics")
            ad1 = Advertisement(
                name="Laptop",
                descriptions="Good laptop",
                price=1000,
                user=user,
                categories=category,
                created_at=datetime.now() - timedelta(days=1),
            )
            ad2 = Advertisement(
                name="Phone",
                descriptions="New phone",
                price=800,
                user=user,
                categories=category,
                created_at=datetime.now(),
            )
            db_session.add_all([user, category, ad1, ad2])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/adv/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["name"] in ["Laptop", "Phone"]

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_advertisements_pagination(
    async_client: AsyncClient,
    db_session,
):
    """Тест пагинации"""
    try:
        async with db_session.begin():
            user = User(
                name="test",
                surname="test",
                email="test2@example.com",
                hashed_password="pass",
            )
            category = Category(name="Books")
            for i in range(15):
                ad = Advertisement(
                    name=f"Book {i}",
                    descriptions=f"Description {i}",
                    price=100 + i,
                    user=user,
                    categories=category,
                )
                db_session.add(ad)
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/adv/?page=1&size=5", headers=headers)
        data = response.json()
        assert len(data["items"]) == 5
        assert data["page"] == 1
        assert data["size"] == 5
        assert data["total"] == 15

        response = await async_client.get("/adv/?page=2&size=5", headers=headers)
        data = response.json()
        assert len(data["items"]) == 5

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_advertisements_price_filters(
    async_client: AsyncClient,
    db_session,
):
    """Тест фильтрации по цене"""
    try:
        async with db_session.begin():
            user = User(
                name="test",
                surname="test",
                email="test3@example.com",
                hashed_password="pass",
            )
            category = Category(name="Cars")
            ad1 = Advertisement(
                name="Car A",
                descriptions="test",
                price=10000,
                user=user,
                categories=category,
            )
            ad2 = Advertisement(
                name="Car B",
                descriptions="test",
                price=20000,
                user=user,
                categories=category,
            )
            ad3 = Advertisement(
                name="Car C",
                descriptions="test",
                price=30000,
                user=user,
                categories=category,
            )
            db_session.add_all([user, category, ad1, ad2, ad3])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/adv/?min_price=15000", headers=headers)
        data = response.json()
        assert data["total"] == 2
        assert all(ad["price"] >= 15000 for ad in data["items"])

        response = await async_client.get("/adv/?max_price=25000", headers=headers)
        data = response.json()
        assert data["total"] == 2
        assert all(ad["price"] <= 25000 for ad in data["items"])

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_advertisements_category_filter(
    async_client: AsyncClient,
    db_session,
):
    """Тест фильтрации по категории"""
    try:
        async with db_session.begin():
            user = User(
                name="test",
                surname="test",
                email="test4@example.com",
                hashed_password="pass",
            )
            cat1 = Category(name="Electronics")
            cat2 = Category(name="Furniture")
            ad1 = Advertisement(
                name="TV", descriptions="test", price=500, user=user, categories=cat1
            )
            ad2 = Advertisement(
                name="Chair", descriptions="test", price=100, user=user, categories=cat2
            )
            db_session.add_all([user, cat1, cat2, ad1, ad2])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/adv/?category=elec", headers=headers)
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "TV"

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_advertisements_sorting(
    async_client: AsyncClient,
    db_session,
):
    """Тест сортировки"""
    try:
        async with db_session.begin():
            user = User(
                name="test",
                surname="test",
                email="test5@example.com",
                hashed_password="pass",
            )
            category = Category(name="Toys")
            now = datetime.now()
            ad1 = Advertisement(
                name="Toy A",
                price=50,
                descriptions="test",
                user=user,
                categories=category,
                created_at=now - timedelta(days=2),
                updated_at=now - timedelta(days=1),
            )
            ad2 = Advertisement(
                name="Toy B",
                price=30,
                descriptions="test",
                user=user,
                categories=category,
                created_at=now - timedelta(days=1),
                updated_at=now,
            )
            db_session.add_all([user, category, ad1, ad2])
            await db_session.commit()

        token = create_access_token(data={"sub": user.email, "id": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/adv/?sort_by_create=true", headers=headers)
        data = response.json()
        assert data["items"][0]["name"] == "Toy B"

        response = await async_client.get("/adv/?price_ascending=true", headers=headers)
        data = response.json()
        assert data["items"][0]["price"] == 30

        response = await async_client.get(
            "/adv/?price_descending=true", headers=headers
        )
        data = response.json()
        assert data["items"][0]["price"] == 50

    finally:
        async with db_session.begin():
            await db_session.execute(delete(Advertisement))
            await db_session.execute(delete(Category))
            await db_session.execute(delete(User))


@pytest.mark.asyncio
async def test_get_advertisements_unauthorized(
    async_client: AsyncClient,
):
    """Тест без авторизации"""
    response = await async_client.get("/adv/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
