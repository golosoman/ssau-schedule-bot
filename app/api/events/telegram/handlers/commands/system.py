from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.api.events.telegram.handlers.shared import build_status_message, load_user
from app.app_layer.interfaces.notifications.notifier.interface import Notifier
from app.app_layer.use_cases.register_user import RegisterUserUseCase
from app.di import Container
from app.domain.messages.info import InfoMessage

router = Router(name="system")


@router.message(Command("start"))
@inject
async def handle_start(
    message: Message,
    register_use_case: RegisterUserUseCase = Provide[Container.register_user_use_case],
    notifier: Notifier = Provide[Container.notifier],
) -> None:
    await load_user(message, register_use_case)
    await notifier.send(
        message.chat.id,
        InfoMessage(
            title="Добро пожаловать",
            lines=[
                "Введи /auth ЛОГИН ПАРОЛЬ, чтобы сохранить доступ.",
                "Команды: /help, /status, /schedule, /tomorrow, /next.",
            ],
        ),
    )


@router.message(Command("help"))
@inject
async def handle_help(
    message: Message,
    notifier: Notifier = Provide[Container.notifier],
) -> None:
    await notifier.send(
        message.chat.id,
        InfoMessage(
            title="Команды",
            lines=[
                "/start - регистрация",
                "/auth ЛОГИН ПАРОЛЬ - сохранить доступ",
                "/subgroup 1|2|all - выбрать подгруппу",
                "/notify on|off - уведомления",
                "/status - текущие настройки",
                "/schedule - расписание на сегодня",
                "/tomorrow - расписание на завтра",
                "/next - ближайшая пара",
                "/notify_test - тестовое уведомление",
                "/sync - принудительно обновить расписание",
            ],
        ),
    )


@router.message(Command("status"))
@inject
async def handle_status(
    message: Message,
    register_use_case: RegisterUserUseCase = Provide[Container.register_user_use_case],
    notifier: Notifier = Provide[Container.notifier],
) -> None:
    user = await load_user(message, register_use_case)
    await notifier.send(message.chat.id, build_status_message(user))
