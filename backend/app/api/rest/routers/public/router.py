from fastapi import APIRouter

from app.api.rest.routers.public.v1.router import router as v1_router

router = APIRouter(prefix="/public", tags=["Public"])
router.include_router(v1_router)
