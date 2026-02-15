from fastapi import FastAPI

from app.api.rest.exception_handler import register_exception_handlers
from app.api.rest.init_routes import init_routes
from app.di import Container
from app.infra.observability.metrics import start_metrics_server
from app.infra.observability.telemetry import configure_telemetry
from app.logging.config import configure_logging


def create_app() -> FastAPI:
    container = Container()
    settings = container.settings()
    configure_logging(settings)
    configure_telemetry(settings)
    if settings.metrics.enabled:
        start_metrics_server(settings.metrics.host, settings.metrics.port)

    app = FastAPI()
    app.state.container = container

    @app.on_event("startup")
    async def on_startup() -> None:
        engine = container.engine()
        app.state.engine = engine

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        engine = getattr(app.state, "engine", None)
        if engine is not None:
            await engine.dispose()

    register_exception_handlers(app)
    init_routes(app)
    return app
