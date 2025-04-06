from fastapi import APIRouter, Depends, HTTPException, status
from src.dto.user_dto import UserDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import User

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserDTO,
)
async def create_user(data: UserDTO, session: AsyncSession = Depends(get_async_db)):
    new_user = User(**data.model_dump())
    try:
        await session.add(new_user)
        await session.commit()
    except Exception as exp:
        print(exp)
        return None

    return new_user
