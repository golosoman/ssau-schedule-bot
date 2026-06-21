from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.api.rest.routers as routers_package
from app.api.rest.exception_handler import register_exception_handlers
from app.api.rest.init_routes import init_routes
from app.di.container import di_scope
from app.infra.observability.metrics.server import start_metrics_server
from app.infra.observability.telemetry.tracing import configure_telemetry
from app.logging.config import configure_logging
from app.settings.config import settings


def create_app() -> FastAPI:
    configure_logging(settings)
    configure_telemetry(settings)
    if settings.metrics.enabled:
        start_metrics_server(settings.metrics.host, settings.api.metrics_port)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with di_scope(wiring_params={"packages": [routers_package]}) as container:
            app.state.container = container
            yield

    app = FastAPI(
        title=settings.api.title,
        docs_url=settings.api.docs_url,
        redoc_url=settings.api.redoc_url,
        openapi_url=settings.api.openapi_url,
        lifespan=lifespan,
    )
    register_exception_handlers(app)
    init_routes(app)
    return app
