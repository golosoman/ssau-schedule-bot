from collections.abc import Callable

from app.app_layer.interfaces.use_cases.register_user.dto.input import (
    RegisterUserUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.register_user.dto.output import (
    RegisterUserUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.register_user.interface import (
    IRegisterUserUseCase,
)
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.domain.entities.users import SsauUser, TelegramUser, User


class RegisterUserUseCase(IRegisterUserUseCase):
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
    ) -> None:
        self._uow_factory = uow_factory

    async def execute(
        self,
        input_dto: RegisterUserUseCaseInputDTO,
    ) -> RegisterUserUseCaseOutputDTO:
        async with self._uow_factory() as uow:
            existing = await uow.users.get_by_chat_id(input_dto.chat_id)
            if existing is not None:
                if existing.telegram.display_name != input_dto.display_name:
                    existing.telegram.display_name = input_dto.display_name
                    return RegisterUserUseCaseOutputDTO(user=await uow.users.upsert(existing))
                return RegisterUserUseCaseOutputDTO(user=existing)

            user = User(
                id=None,
                telegram=TelegramUser(
                    chat_id=input_dto.chat_id,
                    display_name=input_dto.display_name,
                    notify_enabled=True,
                ),
                ssau=SsauUser(
                    credentials=None,
                    profile=None,
                ),
            )
            return RegisterUserUseCaseOutputDTO(user=await uow.users.upsert(user))
