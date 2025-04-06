from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.user_dto import UserGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import User
from src.utils.security import get_current_user

router = APIRouter()


@router.patch(
    "/ban/{user_id}", status_code=status.HTTP_200_OK, response_model=UserGetDTO
)
async def user_ban(
    user_id: int,
    session: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
) -> UserGetDTO:
    try:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot ban himself"
            )
        user.is_banned = True

        session.add(user)
        await session.commit()
        await session.refresh(user)

    except HTTPException:
        raise

    return user
