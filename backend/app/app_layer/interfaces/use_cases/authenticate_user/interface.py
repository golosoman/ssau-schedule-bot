from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.authenticate_user.dto import (
    AuthenticateUserUseCaseInputDTO,
    AuthenticateUserUseCaseOutputDTO,
)


class IAuthenticateUserUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: AuthenticateUserUseCaseInputDTO,
    ) -> AuthenticateUserUseCaseOutputDTO:
        raise NotImplementedError
