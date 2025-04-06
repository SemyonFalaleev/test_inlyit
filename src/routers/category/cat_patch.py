from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.cat_dto import CategoryUpdateDTO, CategoryGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Category

router = APIRouter()


@router.patch("/{cat_id}",
        status_code=status.HTTP_200_OK,
        response_model=CategoryGetDTO
        )
async def patch_category(cat_id: int,
                     data: CategoryUpdateDTO,
                     session: AsyncSession = Depends(get_async_db)
                        ) -> CategoryUpdateDTO:
    try: 
        result = await session.execute(select(Category).where(Category.id == cat_id))
        obj = result.scalar_one_or_none()

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)

        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        
        
    except HTTPException:
        raise
    
    return  obj