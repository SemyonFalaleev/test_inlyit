from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select
from src.db.models.category import Category
from src.dto.adv_dto import AdvertisementGetMinDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Advertisement
from src.schemas.paginate import PaginatedResponse
from src.schemas.deps import pagination_params

from src.utils.security import check_auth

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_auth)],
    response_model=PaginatedResponse[AdvertisementGetMinDTO],
)
async def get_advertisement_all(
    pagination: dict = Depends(pagination_params),
    max_price: Optional[int] = Query(
        description="Выводит все объявление цена которых " "меньше указанного значения",
        default=None,
    ),
    min_price: Optional[int] = Query(
        description="Выводит все объявление цена которых " "больше указанного значения",
        default=None,
    ),
    category: Optional[str] = Query(
        description="Выводит все объявления название категории"
        " которых содержит введённую строку",
        default=None,
    ),
    sort_by_create: Optional[bool] = Query(
        description="Сортирует объявления по дате создания, по возрастанию",
        default=False,
    ),
    sort_by_update: Optional[bool] = Query(
        description="Сортирует объявления по дате последнего изменения, "
        "по возрастанию",
        default=False,
    ),
    price_ascending: Optional[bool] = Query(
        description="Сортирует объявления по цене, " "по возрастанию", default=False
    ),
    price_descending: Optional[bool] = Query(
        description="Сортирует объявления по цене, " "по убыванию", default=False
    ),
    session: AsyncSession = Depends(get_async_db),
) -> PaginatedResponse[AdvertisementGetMinDTO]:
    try:

        query = select(Advertisement).join(Advertisement.categories)

        if category:
            query = query.where(Category.name.ilike(f"%{category}%"))
        if max_price:
            query = query.where(Advertisement.price <= max_price)
        if min_price:
            query = query.where(Advertisement.price >= min_price)
        if sort_by_create:
            query = query.order_by(desc(Advertisement.created_at))
        if sort_by_update:
            query = query.order_by(desc(Advertisement.updated_at))
        if price_descending:
            query = query.order_by(desc(Advertisement.price))
        if price_ascending:
            query = query.order_by(Advertisement.price)

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query)

        paginated_query = query.offset(
            (pagination["page"] - 1) * pagination["size"]
        ).limit(pagination["size"])
        result = await session.execute(paginated_query)
        items = result.scalars().all()

        advertisements = []

        for item in items:
            await session.refresh(item, ["categories"])
            category_name = item.categories.name

            advertisements.append(
                AdvertisementGetMinDTO.model_validate(
                    {**item.__dict__, "category_name": category_name},
                    from_attributes=True,
                )
            )

        return PaginatedResponse.create(
            items=advertisements,
            total=total,
            page=pagination["page"],
            size=pagination["size"],
        )
    except HTTPException:
        raise
