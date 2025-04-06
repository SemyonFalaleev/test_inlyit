from pydantic import BaseModel, EmailStr, SecretStr


class UserLoginDTO(BaseModel):
    username: EmailStr
    password: SecretStr
