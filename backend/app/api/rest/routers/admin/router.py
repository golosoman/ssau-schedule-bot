from fastapi import APIRouter, Depends

from app.api.rest.auth.dependencies import require_admin_token
from app.api.rest.routers.admin.v1.router import router as v1_router

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin_token)],
)
router.include_router(v1_router)
