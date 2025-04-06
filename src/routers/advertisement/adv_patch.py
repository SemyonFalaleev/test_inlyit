from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.models.category import Category
from src.db.models.user import User
from src.dto.adv_dto import AdvertisementUpdateDTO, AdvertisementGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Advertisement
from src.dto.cat_dto import CategoryDTO
from src.dto.user_dto import UserGetDTO
from sqlalchemy.orm import selectinload
from src.utils.security import (
    check_admin_or_yours,
    check_admin,
    check_auth,
    get_current_user,
)

router = APIRouter()


@router.patch(
    "/{adv_id}",
    dependencies=[Depends(check_auth)],
    status_code=status.HTTP_200_OK,
    response_model=AdvertisementGetDTO,
)
async def patch_advertisement(
    adv_id: int,
    data: AdvertisementUpdateDTO,
    cat_id: Optional[int] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_db),
) -> AdvertisementGetDTO:
    try:
        result = await session.execute(
            select(Advertisement).where(Advertisement.id == adv_id)
        )
        obj = result.scalar_one_or_none()

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found"
            )

        await check_admin_or_yours(obj.id, user, Advertisement, session)

        if cat_id:
            result_cat = await session.execute(
                select(Category).where(Category.id == cat_id)
            )
            obj_cat = result_cat.scalar_one_or_none()
            if obj_cat == None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
                )
            obj.category_id = cat_id

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(obj, field, value)

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        result = await session.execute(
            select(Advertisement)
            .where(Advertisement.id == adv_id)
            .options(selectinload(Advertisement.categories))
        )
        new_obj = result.scalar_one()

        adv_data = {
            **new_obj.__dict__,
            "user": UserGetDTO.model_validate(user, from_attributes=True),
            "category": CategoryDTO.model_validate(
                new_obj.categories, from_attributes=True
            ),
        }

        return AdvertisementGetDTO.model_validate(adv_data)

    except HTTPException:
        raise
