from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand
from dependency_injector import providers

import app.api.events.telegram.handlers as handlers_package
import app.api.events.telegram.handlers.commands as commands_package
from app.api.events.telegram.handlers import router as handlers_router
from app.api.events.telegram.middlewares import RequestIdMiddleware
from app.di import Container
from app.infra.observability.metrics import start_metrics_server
from app.infra.observability.telemetry import configure_telemetry
from app.logging.config import configure_logging


async def _set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Регистрация"),
        BotCommand(command="help", description="Справка"),
        BotCommand(command="auth", description="Сохранить доступ"),
        BotCommand(command="subgroup", description="Подгруппа 1|2|all"),
        BotCommand(command="status", description="Текущие настройки"),
        BotCommand(command="schedule", description="Расписание на сегодня"),
        BotCommand(command="tomorrow", description="Расписание на завтра"),
        BotCommand(command="next", description="Ближайшая пара"),
        BotCommand(command="notify", description="Уведомления on/off"),
        BotCommand(command="notify_test", description="Тест уведомления"),
        BotCommand(command="sync", description="Обновить расписание"),
    ]
    await bot.set_my_commands(commands)


async def run_bot() -> None:
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

    try:
        container.telegram_bot.override(providers.Object(bot))
        container.wire(packages=[handlers_package, commands_package])

        dispatcher = Dispatcher()
        dispatcher.message.middleware(RequestIdMiddleware())
        dispatcher.include_router(handlers_router)

        await _set_bot_commands(bot)
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await engine.dispose()
