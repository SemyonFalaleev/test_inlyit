from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.models.review import Review
from src.db.models.user import User
from src.db.base import AsyncSession, get_async_db
from src.dto.review_dto import ReviewGetDTO, ReviewUpdateDTO
from src.utils.security import check_admin_or_yours, get_current_user

router = APIRouter()


@router.patch("/{rev_id}", status_code=status.HTTP_200_OK, response_model=ReviewGetDTO)
async def change_review(
    rev_id: int,
    data: ReviewUpdateDTO,
    session: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
) -> ReviewUpdateDTO:
    try:
        result = await session.execute(select(Review).where(Review.id == rev_id))
        obj = result.scalar_one_or_none()

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )

        await check_admin_or_yours(obj.id, user, Review, session)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return obj
    except HTTPException:
        raise
