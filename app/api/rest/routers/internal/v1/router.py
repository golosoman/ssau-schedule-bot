from fastapi import APIRouter

from app.api.rest.routers.internal.v1.ping.endpoints import router as ping_router

router = APIRouter(prefix="/v1")
router.include_router(ping_router)
