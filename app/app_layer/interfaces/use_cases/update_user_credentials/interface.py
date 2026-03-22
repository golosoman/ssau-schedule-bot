from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.update_user_credentials.dto.input import (
    UpdateUserCredentialsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.dto.output import (
    UpdateUserCredentialsUseCaseOutputDTO,
)


class IUpdateUserCredentialsUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: UpdateUserCredentialsUseCaseInputDTO,
    ) -> UpdateUserCredentialsUseCaseOutputDTO:
        raise NotImplementedError
