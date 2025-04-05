from pydantic import BaseModel, Field, EmailStr, SecretStr
from typing import Optional


class UserLoginDTO(BaseModel):
    username: EmailStr
    password: SecretStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"