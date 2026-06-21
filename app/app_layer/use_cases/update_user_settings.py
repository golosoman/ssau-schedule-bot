from collections.abc import Callable

from app.app_layer.interfaces.repos.account.dto import (
    AccountSettingsUpdateDTO,
    SsauProfileUpdateDTO,
)
from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.app_layer.interfaces.use_cases.update_user_settings.dto.input import (
    UpdateUserSettingsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_settings.dto.output import (
    UpdateUserSettingsUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_settings.interface import (
    IUpdateUserSettingsUseCase,
)


class UpdateUserSettingsUseCase(IUpdateUserSettingsUseCase):
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        account_repo: IAccountRepository,
    ) -> None:
        self._uow_factory = uow_factory
        self._account_repo = account_repo

    async def execute(
        self,
        input_dto: UpdateUserSettingsUseCaseInputDTO,
    ) -> UpdateUserSettingsUseCaseOutputDTO:
        async with self._uow_factory():
            account = await self._account_repo.get_by_chat_id(input_dto.chat_id)
            if account is None:
                raise RuntimeError("User is not registered.")

            if input_dto.notify_enabled is not None:
                await self._account_repo.update_settings(
                    AccountSettingsUpdateDTO(
                        id=account.settings.id,
                        schedule_notifications_enabled=input_dto.notify_enabled,
                    )
                )

            if input_dto.subgroup is not None or input_dto.user_type is not None:
                profile = account.ssau_profile
                if profile is None:
                    raise RuntimeError("User SSAU profile is required to update settings.")
                await self._account_repo.update_ssau_profile(
                    SsauProfileUpdateDTO(
                        id=profile.id,
                        group_id=profile.group_id,
                        year_id=profile.year_id,
                        group_name=profile.group_name,
                        academic_year_start=profile.academic_year_start,
                        subgroup=(
                            input_dto.subgroup
                            if input_dto.subgroup is not None
                            else profile.subgroup
                        ),
                        user_type=(
                            input_dto.user_type
                            if input_dto.user_type is not None
                            else profile.user_type
                        ),
                    )
                )

            view = await self._account_repo.get_by_chat_id(input_dto.chat_id)
            if view is None:
                raise RuntimeError("Account not found after write.")
            return UpdateUserSettingsUseCaseOutputDTO(account=view)
