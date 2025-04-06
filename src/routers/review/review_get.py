from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.models.review import Review
from src.dto.review_dto import ReviewGetDTO
from src.db.base import AsyncSession, get_async_db

router = APIRouter()


@router.get("/{rev_id}", status_code=status.HTTP_200_OK, response_model=ReviewGetDTO)
async def get_review(
    rev_id: int, session: AsyncSession = Depends(get_async_db)
) -> ReviewGetDTO:
    try:
        result = await session.execute(select(Review).where(Review.id == rev_id))
        obj = result.scalar_one_or_none()

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )

        return obj
    except HTTPException:
        raise
