from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.models.user import User
from src.dto.adv_dto import AdvertisementUpdateDTO, AdvertisementGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Advertisement
from src.utils.security import check_admin_or_yours, check_admin, check_auth, get_current_user

router = APIRouter()


@router.patch("/{adv_id}",
        dependencies=[Depends(check_auth)],
        status_code=status.HTTP_200_OK,
        response_model=AdvertisementGetDTO
        )
async def patch_advertisement(
        adv_id: int,
        data: AdvertisementUpdateDTO,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_db)
        ) -> AdvertisementUpdateDTO:
    try: 
        result = await session.execute(select(Advertisement).where(Advertisement.id == adv_id))
        obj = result.scalar_one_or_none()
        await check_admin_or_yours(obj.id, user, session)

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advertisement not found"
            )
        
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(obj, field, value)

        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        
        
    except HTTPException:
        raise
    
    return  obj