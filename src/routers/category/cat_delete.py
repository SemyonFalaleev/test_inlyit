from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.base import AsyncSession, get_async_db
from src.db.models import Category

router = APIRouter()


@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_category(
    cat_id: int, session: AsyncSession = Depends(get_async_db)
) -> None:
    try:
        result = await session.execute(select(Category).where(Category.id == cat_id))
        obj = result.scalar_one_or_none()

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        await session.delete(obj)
        await session.commit()

    except HTTPException:
        raise

    return None
