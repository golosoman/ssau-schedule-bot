from fastapi import APIRouter, Depends

from app.api.rest.routers.admin.v1.router import router as v1_router
from app.api.rest.security.admin_token import require_admin_token

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin_token)],
)
router.include_router(v1_router)
