from fastapi import APIRouter
from src.routers.auth.sign_up import router as sign_up_router
from src.routers.auth.sign_in import router as sign_in_router

router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(sign_up_router)
router.include_router(sign_in_router)
