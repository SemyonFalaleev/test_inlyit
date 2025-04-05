from pydantic import BaseModel, Field, EmailStr, SecretStr
from typing import Optional


class UserDTO(BaseModel):
    name: str = Field(max_length=100)
    surname: str = Field(max_length=100)
    email: EmailStr
    hashed_password: SecretStr

class UserGetDTO(BaseModel):
    name: str = Field(max_length=100)
    surname: str = Field(max_length=100)
    email: EmailStr
    
    
class UserUpdateDTO(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None

