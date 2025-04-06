from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.user_dto import UserDTO, UserGetDTO, UserUpdateDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import User

router = APIRouter()


@router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserGetDTO)
async def patch_user(
    user_id: int, data: UserUpdateDTO, session: AsyncSession = Depends(get_async_db)
) -> UserGetDTO:
    try:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if data.email:
            result_email = await session.execute(
                select(User).where(User.email.like(f"{data.email}"))
            )
            email = result_email.scalar_one_or_none()
            if email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="this email is already in use",
                )
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return UserGetDTO.model_validate(user, from_attributes=True)
    except HTTPException:
        raise
