from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.base import AsyncSession, get_async_db
from src.db.models import Complaint
from src.utils.security import check_admin, check_admin_or_yours, get_current_user

router = APIRouter()


@router.delete(
    "/{comp_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_complaint(
    comp_id: int,
    session: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_user),
) -> None:
    try:
        result = await session.execute(select(Complaint).where(Complaint.id == comp_id))
        obj = result.scalar_one_or_none()
        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found"
            )
        await check_admin_or_yours(obj.id, user, Complaint, session)

        session.delete(obj)
        await session.commit()

    except HTTPException:
        raise

    return None
