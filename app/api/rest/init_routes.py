from fastapi import FastAPI

from app.api.rest.routers.internal_v1 import router as internal_router
from app.api.rest.routers.probes import router as probes_router
from app.api.rest.routers.resources import router as resources_router


def init_routes(app: FastAPI) -> None:
    app.include_router(probes_router)
    app.include_router(internal_router)
    app.include_router(resources_router)
