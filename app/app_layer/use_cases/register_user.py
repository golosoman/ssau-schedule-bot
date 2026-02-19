from collections.abc import Callable

from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.domain.entities.users import SsauUser, TelegramUser, User


class RegisterUserUseCase:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
    ) -> None:
        self._uow_factory = uow_factory

    async def execute(
        self,
        chat_id: int,
        display_name: str,
    ) -> User:
        async with self._uow_factory() as uow:
            existing = await uow.users.get_by_chat_id(chat_id)
            if existing is not None:
                if existing.telegram.display_name != display_name:
                    existing.telegram.display_name = display_name
                    return await uow.users.upsert(existing)
                return existing

            user = User(
                id=None,
                telegram=TelegramUser(
                    chat_id=chat_id,
                    display_name=display_name,
                    notify_enabled=True,
                ),
                ssau=SsauUser(
                    credentials=None,
                    profile=None,
                ),
            )
            return await uow.users.upsert(user)
