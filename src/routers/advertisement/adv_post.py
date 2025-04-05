from fastapi import APIRouter, Depends, HTTPException, status
from src.db.models.user import User
from src.dto.adv_dto import AdvertisementCreateDTO, AdvertisementGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Advertisement
from src.utils.security import check_auth, get_current_user

router = APIRouter()


@router.post("/", 
        dependencies=[Depends(check_auth)],
        status_code=status.HTTP_201_CREATED,
        response_model=AdvertisementGetDTO,
        )
async def create_advertisement(
        data: AdvertisementCreateDTO, 
        session: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_current_user)
        ) -> AdvertisementGetDTO:
    
    new_obj = Advertisement(**data.model_dump())
    new_obj.user_id = user.id
    try:
        session.add(new_obj)
        await session.commit()
    except Exception as exp:
        raise

    return new_obj

    