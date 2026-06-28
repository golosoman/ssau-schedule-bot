from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.update_user_settings.dto import (
    UpdateUserSettingsUseCaseInputDTO,
    UpdateUserSettingsUseCaseOutputDTO,
)


class IUpdateUserSettingsUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: UpdateUserSettingsUseCaseInputDTO,
    ) -> UpdateUserSettingsUseCaseOutputDTO:
        raise NotImplementedError
