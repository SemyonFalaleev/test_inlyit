from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.user_dto import UserDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import User

router = APIRouter()


@router.get("/{user_id}", 
        status_code=status.HTTP_200_OK,
        response_model=UserDTO
        )
async def get_user(user_id: int,
                   session: AsyncSession = Depends(get_async_db)
                      ) -> UserDTO:
    try: 
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
    except HTTPException:
        raise
    
    return  user