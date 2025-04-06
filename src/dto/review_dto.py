from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, 
                              json_encoders={
                              datetime: lambda v: v.strftime("%d-%m-%Y %H:%M")}
                              )  


class ReviewCreateDTO(ReviewBaseDTO):
    description: str = Field(max_length=1000)

class ReviewGetDTO(ReviewBaseDTO):
    id: int
    description: str = Field(max_length=1000)
    adv_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class ReviewUpdateDTO(ReviewBaseDTO):
    description: str

    
