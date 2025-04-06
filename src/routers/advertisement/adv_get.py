from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.models.category import Category
from src.db.models.user import User
from src.dto.adv_dto import AdvertisementGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Advertisement
from fastapi.security import OAuth2PasswordBearer

from src.dto.cat_dto import CategoryDTO
from src.dto.user_dto import UserGetDTO
from src.utils.security import check_auth

router = APIRouter()


@router.get(
    "/{adv_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_auth)],
    response_model=AdvertisementGetDTO,
)
async def get_advertisement(
    adv_id: int, session: AsyncSession = Depends(get_async_db)
) -> AdvertisementGetDTO:
    try:
        stmt = (
            select(Advertisement, Category, User)
            .join(Category, Advertisement.category_id == Category.id)
            .join(User, Advertisement.user_id == User.id)
            .where(Advertisement.id == adv_id)
        )

        obj = await session.execute(stmt)

        row = obj.one_or_none()

        if row == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Advertisemet not found"
            )

        advertisement, category, username = row

        result = AdvertisementGetDTO.model_validate(
            {
                **advertisement.__dict__,
                "category": CategoryDTO.model_validate(category, from_attributes=True),
                "user": UserGetDTO.model_validate(username, from_attributes=True),
            }
        )

    except HTTPException:
        raise

    return result
