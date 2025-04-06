from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select
from src.db.base import AsyncSession, get_async_db
from src.db.models.complaint import Complaint
from src.schemas.paginate import PaginatedResponse
from src.schemas.deps import pagination_params
from src.dto.comp_dto import ComplaintGetDTO

from src.utils.security import check_admin

router = APIRouter()


@router.get("/", 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(check_admin)],
        response_model=PaginatedResponse[ComplaintGetDTO]
        )
async def get_complaint_all(
        pagination: dict = Depends(pagination_params),
        adv_id: Optional[int] = Query(
            description="Выводит жалобы по конкретному объявлению",
            default=None
        ),
        sort_by_create: Optional[bool] = Query(
            description="Сортирует жалобы по дате создания, по возрастанию",
            default=False
        ) ,
        sort_by_update: Optional[bool] = Query(
            description="Сортирует жалобы по дате последнего изменения, " \
                        "по возрастанию",
            default=False
        ) ,

        session: AsyncSession = Depends(get_async_db)
        ) -> PaginatedResponse[ComplaintGetDTO]:
    try: 

        query = select(Complaint)

        if adv_id:
            query = query.where(Complaint.adv_id == adv_id)
        if sort_by_create:
            query = query.order_by(desc(Complaint.created_at))
        if sort_by_update:
            query = query.order_by(desc(Complaint.updated_at))


        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query)


        paginated_query = query.offset((pagination["page"] - 1) * pagination["size"]).\
                          limit(pagination["size"])
        result = await session.execute(paginated_query)
        items = result.scalars().all()
    
        return PaginatedResponse.create(
            items=items,
            total=total,
            page=pagination["page"],
            size=pagination["size"]
        )
    except HTTPException:
        raise