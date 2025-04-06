from pydantic import BaseModel, Field, SecretStr, EmailStr
from typing import Optional


class UserDTO(BaseModel):
    name: str = Field(max_length=100)
    surname: str = Field(max_length=100)
    email: EmailStr
    hashed_password: SecretStr


class UserGetDTO(BaseModel):
    id: int
    name: str = Field(max_length=100)
    surname: str = Field(max_length=100)
    email: EmailStr
    is_banned: bool
    is_admin: bool


class UserUpdateDTO(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
