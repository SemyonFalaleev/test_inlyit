from fastapi import APIRouter, Depends, HTTPException, status
from src.db.models.user import User
from src.dto.adv_dto import AdvertisementCreateDTO, AdvertisementGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Advertisement
from src.dto.cat_dto import CategoryDTO
from src.dto.user_dto import UserGetDTO
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
        await session.refresh(new_obj, ["categories"])

        adv_data = {
            k: v for k, v in new_obj.__dict__.items() 
            if not k.startswith('_')
        }
        
        adv_data.update({
            "user": UserGetDTO.model_validate(user, from_attributes=True),
            "category": CategoryDTO.model_validate(new_obj.categories, from_attributes=True),
        })
        
        return AdvertisementGetDTO.model_validate(adv_data)
    except Exception as exp:
        raise


    