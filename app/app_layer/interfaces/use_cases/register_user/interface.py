from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.register_user.dto.input import (
    RegisterUserUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.register_user.dto.output import (
    RegisterUserUseCaseOutputDTO,
)


class IRegisterUserUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: RegisterUserUseCaseInputDTO,
    ) -> RegisterUserUseCaseOutputDTO:
        raise NotImplementedError
