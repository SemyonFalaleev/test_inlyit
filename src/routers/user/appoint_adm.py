from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.user_dto import UserGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import User

router = APIRouter()


@router.patch(
    "/adm/{user_id}", status_code=status.HTTP_200_OK, response_model=UserGetDTO
)
async def appoint_adm(
    user_id: int, session: AsyncSession = Depends(get_async_db)
) -> UserGetDTO:
    try:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User is banned"
            )
        user.is_admin = True

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserGetDTO.model_validate(user, from_attributes=True)
    except HTTPException:
        raise
