from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.routers.advertisement.adv_post import router as post_router
from src.routers.advertisement.adv_delete  import router as delete_router
from src.routers.advertisement.adv_get import router as get_router
from src.routers.advertisement.adv_patch import router as patch_router
from src.routers.advertisement.adv_get_all import router as get_all_router

router = APIRouter(prefix="/adv", tags=["Advertisement"])

router.include_router(post_router)
router.include_router(delete_router)
router.include_router(get_router)
router.include_router(patch_router)
router.include_router(get_all_router)