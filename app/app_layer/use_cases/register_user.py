from collections.abc import Callable

from app.app_layer.interfaces.repos.account.dto import (
    AccountSettingsCreateDTO,
    AccountView,
    TelegramIdentityCreateDTO,
    TelegramIdentityUpdateDTO,
)
from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.app_layer.interfaces.use_cases.register_user.dto.input import (
    RegisterUserUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.register_user.dto.output import (
    RegisterUserUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.register_user.interface import (
    IRegisterUserUseCase,
)


class RegisterUserUseCase(IRegisterUserUseCase):
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        account_repo: IAccountRepository,
    ) -> None:
        self._uow_factory = uow_factory
        self._account_repo = account_repo

    async def execute(
        self,
        input_dto: RegisterUserUseCaseInputDTO,
    ) -> RegisterUserUseCaseOutputDTO:
        async with self._uow_factory():
            existing = await self._account_repo.get_by_chat_id(input_dto.chat_id)
            if existing is not None:
                if existing.telegram.display_name == input_dto.display_name:
                    return RegisterUserUseCaseOutputDTO(account=existing)
                await self._account_repo.update_telegram_identity(
                    TelegramIdentityUpdateDTO(
                        id=existing.telegram.id,
                        display_name=input_dto.display_name,
                    )
                )
                return RegisterUserUseCaseOutputDTO(
                    account=await _require_view(self._account_repo, input_dto.chat_id)
                )

            account = await self._account_repo.create_account()
            await self._account_repo.create_telegram_identity(
                TelegramIdentityCreateDTO(
                    account_id=account.id,
                    chat_id=input_dto.chat_id,
                    display_name=input_dto.display_name,
                )
            )
            await self._account_repo.create_settings(
                AccountSettingsCreateDTO(
                    account_id=account.id,
                    schedule_notifications_enabled=True,
                )
            )
            return RegisterUserUseCaseOutputDTO(
                account=await _require_view(self._account_repo, input_dto.chat_id)
            )


async def _require_view(account_repo: IAccountRepository, chat_id: int) -> AccountView:
    view = await account_repo.get_by_chat_id(chat_id)
    if view is None:
        raise RuntimeError("Account not found after write.")
    return view
