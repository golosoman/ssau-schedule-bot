import asyncio

from dependency_injector import providers

import app.api.jobs as jobs_package
from app.api.jobs.scheduler import build_scheduler
from app.di import Container
from app.infra.clients.telegram.bot import create_bot
from app.infra.clients.telegram.settings import TelegramClientSettings
from app.infra.observability.metrics import start_metrics_server
from app.infra.observability.telemetry import configure_telemetry
from app.logging.config import configure_logging
from app.settings.config import settings


async def run_worker() -> None:
    container = Container()
    configure_logging(settings)
    configure_telemetry(settings)
    if settings.metrics.enabled:
        start_metrics_server(settings.metrics.host, settings.metrics.port)

    engine = container.engine()

    bot = create_bot(
        TelegramClientSettings(
            bot_token=settings.telegram.bot_token.get_secret_value(),
            proxy_url=settings.telegram.proxy_url,
        )
    )

    container.telegram_bot.override(providers.Object(bot))
    container.wire(packages=[jobs_package])

    scheduler = None
    try:
        scheduler = build_scheduler()
        scheduler.start()
        await asyncio.Event().wait()
    finally:
        if scheduler is not None:
            scheduler.shutdown(wait=False)
        await bot.session.close()
        await engine.dispose()
