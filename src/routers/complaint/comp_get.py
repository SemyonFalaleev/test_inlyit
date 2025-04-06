from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.models.user import User
from src.dto.comp_dto import ComplaintGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Complaint
from src.utils.security import check_admin_or_yours, get_current_user

router = APIRouter()


@router.get(
    "/{comp_id}", status_code=status.HTTP_200_OK, response_model=ComplaintGetDTO
)
async def get_complaint(
    comp_id: int,
    session: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
) -> ComplaintGetDTO:
    try:

        result = await session.execute(select(Complaint).where(Complaint.id == comp_id))
        obj = result.scalar_one_or_none()
        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
            )
        await check_admin_or_yours(obj.id, user, Complaint, session)

        return ComplaintGetDTO.model_validate(obj, from_attributes=True)
    except HTTPException:
        raise
