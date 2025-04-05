from fastapi import APIRouter, Depends
from src.routers.user.user_post import router as post_router
from src.routers.user.user_delete import router as delete_router
from src.routers.user.user_get import router as get_user
from src.routers.user.user_patch import router as patch_user
from src.utils.security import check_admin

router = APIRouter(prefix="/user", tags=["User"], dependencies=[Depends(check_admin)])

router.include_router(post_router)
router.include_router(delete_router)
router.include_router(get_user)
router.include_router(patch_user)


