from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.comp_dto import ComplaintGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Complaint

router = APIRouter()


@router.get(
    "/{comp_id}", status_code=status.HTTP_200_OK, response_model=ComplaintGetDTO
)
async def get_complaint(
    comp_id: int, session: AsyncSession = Depends(get_async_db)
) -> ComplaintGetDTO:
    try:
        result = await session.execute(select(Complaint).where(Complaint.id == comp_id))
        obj = result.scalar_one_or_none()

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
            )

    except HTTPException:
        raise

    return obj
