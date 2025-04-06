from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class CategoryDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)  
    id: int
    name: str = Field(max_length=100)

class CategoryCreateDTO(BaseModel):
    name: str = Field(max_length=100)
    
class CategoryGetDTO(CategoryCreateDTO):
    id: int

class CategoryUpdateDTO(BaseModel):
    name: Optional[str] = None