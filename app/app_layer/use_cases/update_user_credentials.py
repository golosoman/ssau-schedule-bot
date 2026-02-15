from typing import Callable

from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.domain.entities.user import SsauCredentials, User


class UpdateUserCredentialsUseCase:

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def execute(self, chat_id: int, login: str, password: str) -> User:
        async with self._uow_factory() as uow:
            user = await uow.users.get_by_chat_id(chat_id)
            if user is None:
                raise RuntimeError("User is not registered.")

            user.ssau.credentials = SsauCredentials(login=login, password=password)
            user.ssau.profile = None
            return await uow.users.upsert(user)
