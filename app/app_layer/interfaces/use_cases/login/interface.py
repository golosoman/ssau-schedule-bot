from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.login.dto.input import LoginUseCaseInputDTO
from app.app_layer.interfaces.use_cases.login.dto.output import LoginUseCaseOutputDTO


class ILoginUseCase(ABC):
    @abstractmethod
    async def execute(self, input_dto: LoginUseCaseInputDTO) -> LoginUseCaseOutputDTO:
        raise NotImplementedError
