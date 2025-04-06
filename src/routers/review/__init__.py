from fastapi import APIRouter, Depends
from src.routers.review.review_post import router as post_router
from src.routers.review.review_get import router as get_router
from src.routers.review.review_patch import router as patch_router
from src.routers.review.review_delete import router as deletr_router
from src.routers.review.review_get_all import router as get_all_router


from src.utils.security import check_auth

router = APIRouter(prefix="/review", tags=["Review"], dependencies=[Depends(check_auth)])

router.include_router(post_router)
router.include_router(get_router)
router.include_router(patch_router)
router.include_router(deletr_router)
router.include_router(get_all_router)

