from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from src.db.base import AsyncSession, get_async_db
from src.db.models import User
from src.utils.security import verify_password, create_access_token
from datetime import timedelta
from src.config import settings

router = APIRouter()

@router.post("/login",
             status_code=status.HTTP_200_OK,
             )
async def sign_in(data: OAuth2PasswordRequestForm = Depends(),
                  session: AsyncSession = Depends(get_async_db)
                  ) :
    
    existing_user = await session.execute(
        select(User).where(User.email == data.username))
    user = existing_user.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is not registred"
        )
    if verify_password(data.password, user.hashed_password):
        access_token=create_access_token(user.__dict__, 
                                      timedelta(minutes=settings.token_expires))
        return {"access_token": access_token, "token_type": "bearer"}
 
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect email or password"
        )
    
    