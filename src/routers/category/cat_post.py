from fastapi import APIRouter, Depends, HTTPException, status
from src.dto.cat_dto import CategoryCreateDTO, CategoryGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Category
from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.post("/", 
        status_code=status.HTTP_201_CREATED,
        response_model=CategoryCreateDTO,
        )
async def create_category(data: CategoryCreateDTO, session: AsyncSession = Depends(get_async_db)):
    new_obj = Category(**data.model_dump())
    try:
        session.add(new_obj)
        await session.commit()
        await session.refresh(new_obj)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="A category with this name already exists")      
    return new_obj



    