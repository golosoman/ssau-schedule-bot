from collections.abc import Callable

from app.app_layer.interfaces.repos.account.dto import SsauIdentityCreateDTO
from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.app_layer.interfaces.use_cases.update_user_credentials.dto.input import (
    UpdateUserCredentialsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.dto.output import (
    UpdateUserCredentialsUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.interface import (
    IUpdateUserCredentialsUseCase,
)


class UpdateUserCredentialsUseCase(IUpdateUserCredentialsUseCase):
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        account_repo: IAccountRepository,
    ) -> None:
        self._uow_factory = uow_factory
        self._account_repo = account_repo

    async def execute(
        self,
        input_dto: UpdateUserCredentialsUseCaseInputDTO,
    ) -> UpdateUserCredentialsUseCaseOutputDTO:
        async with self._uow_factory():
            account = await self._account_repo.get_by_chat_id(input_dto.chat_id)
            if account is None:
                raise RuntimeError("User is not registered.")

            # Новые креды сбрасывают старую identity и её профиль (каскад).
            await self._account_repo.delete_ssau_identity(account.account_id)
            await self._account_repo.create_ssau_identity(
                SsauIdentityCreateDTO(
                    account_id=account.account_id,
                    login=input_dto.login,
                    password=input_dto.password,
                )
            )
            view = await self._account_repo.get_by_chat_id(input_dto.chat_id)
            if view is None:
                raise RuntimeError("Account not found after write.")
            return UpdateUserCredentialsUseCaseOutputDTO(account=view)
