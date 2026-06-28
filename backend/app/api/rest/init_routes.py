from fastapi import FastAPI

from app.api.rest.routers.admin.router import router as admin_router
from app.api.rest.routers.internal.router import router as internal_router
from app.api.rest.routers.probes.router import router as probes_router
from app.api.rest.routers.public.router import router as public_router


def init_routes(app: FastAPI) -> None:
    app.include_router(probes_router)
    app.include_router(public_router)
    app.include_router(internal_router)
    app.include_router(admin_router)
