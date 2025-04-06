from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ComplaintBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, 
                              json_encoders={
                              datetime: lambda v: v.strftime("%d-%m-%Y %H:%M")}
                              )  


class ComplaintCreateDTO(ComplaintBaseDTO):
    description: str = Field(max_length=1000)

class ComplaintGetDTO(ComplaintBaseDTO):
    id: int
    description: str = Field(max_length=1000)
    adv_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class ComplaintUpdateDTO(ComplaintBaseDTO):
    description: str

    
