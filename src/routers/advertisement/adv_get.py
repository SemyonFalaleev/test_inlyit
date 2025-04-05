from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.adv_dto import AdvertisementGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Advertisement
from fastapi.security import OAuth2PasswordBearer

from src.utils.security import check_auth

router = APIRouter()


@router.get("/{adv_id}", 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(check_auth)],
        response_model=AdvertisementGetDTO
        )
async def get_advertisement(
        adv_id: int,
        session: AsyncSession = Depends(get_async_db)
        ) -> AdvertisementGetDTO:
    try: 
        result = await session.execute(select(Advertisement).where(Advertisement.id == adv_id))
        obj = result.scalar_one_or_none()

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advertisemet not found"
            )
        
    except HTTPException:
        raise
    
    return  obj