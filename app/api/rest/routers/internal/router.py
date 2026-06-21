from fastapi import APIRouter

from app.api.rest.routers.internal.v1.router import router as v1_router

router = APIRouter(prefix="/internal", tags=["Internal"])
router.include_router(v1_router)
