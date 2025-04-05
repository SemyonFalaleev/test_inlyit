from pydantic import BaseModel, Field
from typing import Optional


class CategoryCreateDTO(BaseModel):
    name: str = Field(max_length=100)
    
class CategoryGetDTO(CategoryCreateDTO):
    id: int

class CategoryUpdateDTO(BaseModel):
    name: Optional[str] = None