import asyncio

import app.api.jobs as jobs_package
from app.api.jobs.scheduler import build_scheduler
from app.di.container import di_scope
from app.infra.observability.metrics.server import start_metrics_server
from app.infra.observability.telemetry.tracing import configure_telemetry
from app.logging.config import configure_logging
from app.settings.config import settings


async def run_worker() -> None:
    configure_logging(settings)
    configure_telemetry(settings)
    if settings.metrics.enabled:
        start_metrics_server(settings.metrics.host, settings.workers.metrics_port)

    async with di_scope(wiring_params={"packages": [jobs_package]}):
        scheduler = build_scheduler()
        scheduler.start()
        try:
            await asyncio.Event().wait()
        finally:
            scheduler.shutdown(wait=False)
