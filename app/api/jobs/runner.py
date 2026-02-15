import asyncio

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from dependency_injector import providers

import app.api.jobs as jobs_package
from app.api.jobs.scheduler import build_scheduler
from app.di import Container
from app.infra.observability.metrics import start_metrics_server
from app.infra.observability.telemetry import configure_telemetry
from app.logging.config import configure_logging


async def run_worker() -> None:
    container = Container()
    settings = container.settings()
    configure_logging(settings)
    configure_telemetry(settings)
    if settings.metrics.enabled:
        start_metrics_server(settings.metrics.host, settings.metrics.port)

    engine = container.engine()

    if settings.telegram.proxy_url:
        session = AiohttpSession(proxy=settings.telegram.proxy_url)
        bot = Bot(token=settings.telegram.bot_token, session=session)
    else:
        bot = Bot(token=settings.telegram.bot_token)

    container.telegram_bot.override(providers.Object(bot))
    container.wire(packages=[jobs_package])

    scheduler = None
    try:
        scheduler = build_scheduler(settings)
        scheduler.start()
        await asyncio.Event().wait()
    finally:
        if scheduler is not None:
            scheduler.shutdown(wait=False)
        await bot.session.close()
        await engine.dispose()
