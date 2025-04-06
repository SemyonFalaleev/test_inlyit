from fastapi import APIRouter, Depends, HTTPException
from src.routers.category.cat_post import router as post_router
from src.routers.category.cat_delete import router as delete_router
from src.routers.category.cat_get import router as get_router
from src.routers.category.cat_patch import router as patch_user
from src.utils.security import check_admin

router = APIRouter(
    prefix="/category", tags=["Category"], dependencies=[Depends(check_admin)]
)

router.include_router(post_router)
router.include_router(delete_router)
router.include_router(get_router)
router.include_router(patch_user)
