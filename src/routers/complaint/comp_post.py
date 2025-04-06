from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.models.advertisement import Advertisement
from src.db.models.complaint import Complaint
from src.db.models.user import User
from src.db.base import AsyncSession, get_async_db
from src.dto.adv_dto import AdvertisementGetMinDTO
from src.dto.comp_dto import ComplaintCreateDTO, ComplaintGetDTO
from src.dto.user_dto import UserGetDTO
from src.utils.security import check_auth, get_current_user
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.post("/{adv_id}", 
        dependencies=[Depends(check_auth)],
        status_code=status.HTTP_201_CREATED,
        response_model=ComplaintGetDTO,
        )
async def create_complaint(
        adv_id: int,
        data: ComplaintCreateDTO, 
        session: AsyncSession = Depends(get_async_db),
        user: User = Depends(get_current_user)
        ) -> ComplaintGetDTO:
    try:

        result = await session.execute(select(Advertisement).where(Advertisement.id == adv_id))
        adv = result.scalar_one_or_none()
        
        if adv == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Advertisement not found"
            )
        if adv.user_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot leave complaints about your ads"
            )
        
        new_obj = Complaint(**data.model_dump(),
                        user_id = user.id,
                        adv_id = adv_id)
    
        session.add(new_obj)
        await session.commit()
        await session.refresh(new_obj)
    
        return ComplaintGetDTO.model_validate(new_obj, from_attributes=True)

    except Exception as exp:
        raise