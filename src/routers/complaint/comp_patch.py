from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.models.complaint import Complaint

from src.db.models.user import User
from src.db.base import AsyncSession, get_async_db
from src.dto.comp_dto import ComplaintGetDTO, ComplaintUpdateDTO
from src.utils.security import check_admin_or_yours, get_current_user

router = APIRouter()


@router.patch(
    "/{comp_id}", status_code=status.HTTP_200_OK, response_model=ComplaintGetDTO
)
async def change_complaint(
    comp_id: int,
    data: ComplaintUpdateDTO,
    session: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
) -> ComplaintUpdateDTO:
    try:
        result = await session.execute(select(Complaint).where(Complaint.id == comp_id))
        obj = result.scalar_one_or_none()
        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
            )
        await check_admin_or_yours(obj.id, user, Complaint, session)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return obj
    except HTTPException:
        raise
