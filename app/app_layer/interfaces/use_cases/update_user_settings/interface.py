from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.update_user_settings.dto.input import (
    UpdateUserSettingsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_settings.dto.output import (
    UpdateUserSettingsUseCaseOutputDTO,
)


class IUpdateUserSettingsUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: UpdateUserSettingsUseCaseInputDTO,
    ) -> UpdateUserSettingsUseCaseOutputDTO:
        raise NotImplementedError
