from collections.abc import Callable

from app.app_layer.interfaces.use_cases.update_user_credentials.dto.input import (
    UpdateUserCredentialsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.dto.output import (
    UpdateUserCredentialsUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.interface import (
    IUpdateUserCredentialsUseCase,
)
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.domain.entities.users import SsauCredentials


class UpdateUserCredentialsUseCase(IUpdateUserCredentialsUseCase):
    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def execute(
        self,
        input_dto: UpdateUserCredentialsUseCaseInputDTO,
    ) -> UpdateUserCredentialsUseCaseOutputDTO:
        async with self._uow_factory() as uow:
            user = await uow.users.get_by_chat_id(input_dto.chat_id)
            if user is None:
                raise RuntimeError("User is not registered.")

            user.ssau.credentials = SsauCredentials(
                login=input_dto.login,
                password=input_dto.password,
            )
            user.ssau.profile = None
            return UpdateUserCredentialsUseCaseOutputDTO(user=await uow.users.upsert(user))
