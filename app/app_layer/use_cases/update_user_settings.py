from collections.abc import Callable

from app.app_layer.interfaces.use_cases.update_user_settings.dto.input import (
    UpdateUserSettingsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_settings.dto.output import (
    UpdateUserSettingsUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_settings.interface import (
    IUpdateUserSettingsUseCase,
)
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork


class UpdateUserSettingsUseCase(IUpdateUserSettingsUseCase):
    def __init__(self, uow_factory: Callable[[], IUnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def execute(
        self,
        input_dto: UpdateUserSettingsUseCaseInputDTO,
    ) -> UpdateUserSettingsUseCaseOutputDTO:
        async with self._uow_factory() as uow:
            user = await uow.users.get_by_chat_id(input_dto.chat_id)
            if user is None:
                raise RuntimeError("User is not registered.")

            if input_dto.subgroup is not None or input_dto.user_type is not None:
                if user.ssau.profile is None:
                    raise RuntimeError("User SSAU profile is required to update settings.")
                updates = {}
                if input_dto.subgroup is not None:
                    updates["subgroup"] = input_dto.subgroup
                if input_dto.user_type is not None:
                    updates["user_type"] = input_dto.user_type
                if updates:
                    details = user.ssau.profile.profile_details.model_copy(update=updates)
                    user.ssau.profile = user.ssau.profile.model_copy(
                        update={"profile_details": details}
                    )
            if input_dto.notify_enabled is not None:
                user.telegram.notify_enabled = input_dto.notify_enabled

            return UpdateUserSettingsUseCaseOutputDTO(user=await uow.users.upsert(user))
