from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.adv_dto import AdvertisementGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Advertisement

from src.dto.cat_dto import CategoryDTO
from src.dto.review_dto import ReviewGetDTO
from src.dto.user_dto import UserGetDTO
from src.utils.security import check_auth
from sqlalchemy.orm import joinedload, selectinload

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
            select(Advertisement)
            .where(Advertisement.id == adv_id)
            .options(
                joinedload(Advertisement.categories),
                joinedload(Advertisement.user),
                selectinload(Advertisement.reviews),
            )
        )

        obj = await session.execute(stmt)

        advertisement = obj.scalars().one_or_none()

        if advertisement == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Advertisemet not found"
            )

        result = AdvertisementGetDTO.model_validate(
            {
                **advertisement.__dict__,
                "category": CategoryDTO.model_validate(
                    advertisement.categories, from_attributes=True
                ),
                "user": UserGetDTO.model_validate(
                    advertisement.user, from_attributes=True
                ),
                "reviews": [
                    ReviewGetDTO.model_validate(review, from_attributes=True)
                    for review in advertisement.reviews
                ],
            }
        )

    except HTTPException:
        raise

    return result
