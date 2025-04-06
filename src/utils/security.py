from typing import List, Type
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

from sqlalchemy import select
from src.config import settings
from fastapi import Depends, HTTPException, Request, status
from src.db.base import AsyncSession
from src.db.db_func import get_user_from_db
from src.db.models.user import User
from src.db.base import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
UNPROTECTED_ROUTES: List[str] = ["/login", "/register", "/docs", "/openapi.json"]


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    try:
        if data.get("is_admin") == False:
            is_admin = 0
        else:
            is_admin = 1
        payload = {
            "sub": str(data.get("id")),
            "id": data.get("id"),
            "is_admin": is_admin,
        }

        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.token_expires)
        )
        payload.update({"exp": expire})
        return jwt.encode(
            payload, settings.secret_key_jwt, algorithm=settings.algoritm_jwt
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token creation error: {str(e)}",
        )


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token.encode("utf-8"),
            settings.secret_key_jwt,
            algorithms=[settings.algoritm_jwt],
        )
        user_id: str = payload.get("id")
        if not user_id:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception

    user = await get_user_from_db(user_id)
    if not user:
        raise credentials_exception
    return user


async def check_auth(request: Request, user: User = Depends(get_current_user)):
    if request.url.path not in UNPROTECTED_ROUTES:
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are banned",
            )
        return user


async def check_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges",
        )
    return user


async def check_admin_or_yours(
    obj_id: int, user: User, model: Type[Base], db: AsyncSession  # type: ignore
):
    try:
        await check_admin(user)
        return user
    except HTTPException as e:
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are banned",
            )
        if e.status_code == status.HTTP_403_FORBIDDEN:
            result = await db.execute(
                select(model).where(model.id == obj_id, model.user_id == user.id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient privileges",
                )
            return user
        else:
            raise
