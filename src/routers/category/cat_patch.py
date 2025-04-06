from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from src.dto.cat_dto import CategoryUpdateDTO, CategoryGetDTO
from src.db.base import AsyncSession, get_async_db
from src.db.models import Category

router = APIRouter()


@router.patch(
    "/{cat_id}", status_code=status.HTTP_200_OK, response_model=CategoryGetDTO
)
async def patch_category(
    cat_id: int, data: CategoryUpdateDTO, session: AsyncSession = Depends(get_async_db)
) -> CategoryUpdateDTO:
    try:
        result = await session.execute(select(Category).where(Category.id == cat_id))
        obj = result.scalar_one_or_none()

        if obj == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        if data.name:
            result_cat = await session.execute(
                select(Category).where(Category.name.ilike(f"{data.name}"))
            )
            cat = result_cat.scalar_one_or_none()
            if cat:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A category with this name" "already exists",
                )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)

        session.add(obj)
        await session.commit()
        await session.refresh(obj)

        return CategoryGetDTO.model_validate(obj, from_attributes=True)

    except HTTPException:
        raise
