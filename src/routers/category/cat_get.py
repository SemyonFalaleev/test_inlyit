from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.cat_dto import CategoryGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Category

router = APIRouter()


@router.get("/{cat_id}", status_code=status.HTTP_200_OK, response_model=CategoryGetDTO)
async def get_category(
    cat_id: int, session: AsyncSession = Depends(get_async_db)
) -> CategoryGetDTO:
    try:
        result = await session.execute(select(Category).where(Category.id == cat_id))
        obj = result.scalar_one_or_none()

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

    except HTTPException:
        raise

    return obj
