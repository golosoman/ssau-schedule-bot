from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

import app.api.events.telegram.handlers as handlers_package
import app.api.events.telegram.handlers.commands as commands_package
from app.api.events.telegram.handlers.router import router as handlers_router
from app.api.events.telegram.middlewares import RequestIdMiddleware
from app.di.container import di_scope, resolve_resource
from app.infra.observability.metrics.server import start_metrics_server
from app.infra.observability.telemetry.tracing import configure_telemetry
from app.logging.config import configure_logging
from app.settings.config import settings


async def _set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Регистрация"),
        BotCommand(command="help", description="Справка"),
        BotCommand(command="auth", description="Вход через СНИУ"),
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
    configure_logging(settings)
    configure_telemetry(settings)
    if settings.metrics.enabled:
        start_metrics_server(settings.metrics.host, settings.telegram.metrics_port)

    wiring_params = {"packages": [handlers_package, commands_package]}
    async with di_scope(wiring_params=wiring_params) as container:
        bot = await resolve_resource(container.telegram.bot)
        dispatcher = Dispatcher(storage=MemoryStorage())
        dispatcher.message.middleware(RequestIdMiddleware())
        dispatcher.include_router(handlers_router)

        await _set_bot_commands(bot)
        await dispatcher.start_polling(bot)
