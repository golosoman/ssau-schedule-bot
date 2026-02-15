from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dependency_injector.wiring import Provide, inject

from app.api.events.telegram.handlers.shared import format_status, load_user
from app.app_layer.use_cases.register_user import RegisterUserUseCase
from app.di import Container

router = Router(name="system")


@router.message(Command("start"))
@inject
async def handle_start(
    message: Message,
    register_use_case: RegisterUserUseCase = Provide[Container.register_user_use_case],
) -> None:
    await load_user(message, register_use_case)
    await message.answer(
        "Привет! Введи /auth ЛОГИН ПАРОЛЬ, чтобы сохранить доступ.\n"
        "Команды: /help, /status, /schedule, /tomorrow, /next."
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "Команды:\n"
        "/start - регистрация\n"
        "/auth ЛОГИН ПАРОЛЬ - сохранить доступ\n"
        "/subgroup 1|2 - выбрать подгруппу\n"
        "/notify on|off - уведомления\n"
        "/status - текущие настройки\n"
        "/schedule - расписание на сегодня\n"
        "/tomorrow - расписание на завтра\n"
        "/next - ближайшая пара\n"
        "/notify_test - тестовое уведомление\n"
        "/sync - принудительно обновить расписание"
    )


@router.message(Command("status"))
@inject
async def handle_status(
    message: Message,
    register_use_case: RegisterUserUseCase = Provide[Container.register_user_use_case],
) -> None:
    user = await load_user(message, register_use_case)
    await message.answer(format_status(user))
