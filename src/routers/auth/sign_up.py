from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.user_dto import UserDTO, UserGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import User
from src.utils.security import get_password_hash

router = APIRouter()


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserGetDTO
)
async def sign_up(data: UserDTO, session: AsyncSession = Depends(get_async_db)):

    existing_user = await session.execute(select(User).where(User.email == data.email))

    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(data.hashed_password.get_secret_value())
    data.hashed_password = hashed_password
    new_user = User(**data.model_dump())

    try:
        session.add(new_user)
        await session.commit()
    except Exception as exp:
        raise

    return new_user
