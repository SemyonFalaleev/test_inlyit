from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AdvertisementUpdateDTO(BaseModel):
    name: Optional[str] = None
    descriptions: Optional[str] = None
    price: Optional[int] = None
    category_id: Optional[str] = None

class AdvertisementBaseDTO(BaseModel):
    name: str = Field(max_length=150)
    category_id: int

    
class AdvertisementCreateDTO(AdvertisementBaseDTO):
    descriptions: str
    price: Optional[int] = None

class AdvertisementGetDTO(AdvertisementCreateDTO):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int



