from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional
from datetime import datetime
from src.dto.cat_dto import CategoryDTO
from src.dto.user_dto import UserGetDTO


class AdertisementBaseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.strftime("%d-%m-%Y %H:%M")},
    )


class AdvertisementUpdateDTO(AdertisementBaseDTO):
    name: Optional[str] = None
    descriptions: Optional[str] = None
    price: Optional[int] = None


class AdvertisementBaseDTO(AdertisementBaseDTO):
    name: str = Field(max_length=150)
    category_id: int


class AdvertisementCreateDTO(AdvertisementBaseDTO):
    descriptions: str
    price: Optional[int] = None


class AdvertisementGetMinDTO(AdertisementBaseDTO):
    id: int
    name: str
    price: int
    category_name: str
    created_at: datetime
    updated_at: datetime


class AdvertisementGetDTO(AdertisementBaseDTO):
    id: int
    name: str
    descriptions: str
    price: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    user: UserGetDTO
    category: CategoryDTO
