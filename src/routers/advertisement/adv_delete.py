from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.db.base import AsyncSession, get_async_db
from src.db.models import Advertisement
from src.db.models.user import User
from src.utils.security import check_admin_or_yours, check_auth, get_current_user

router = APIRouter()


@router.delete(
    "/{adv_id}",
    dependencies=[Depends(check_auth)],
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_advertisement(
    adv_id: int,
    session: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_current_user),
) -> None:
    try:
        result = await session.execute(
            select(Advertisement).where(Advertisement.id == adv_id)
        )
        obj = result.scalar_one_or_none()
        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found"
            )
        await check_admin_or_yours(obj.id, user, Advertisement, session)

        await session.delete(obj)
        await session.commit()

    except HTTPException:
        raise

    return None
