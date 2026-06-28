from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.update_user_credentials.dto import (
    UpdateUserCredentialsUseCaseInputDTO,
    UpdateUserCredentialsUseCaseOutputDTO,
)


class IUpdateUserCredentialsUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: UpdateUserCredentialsUseCaseInputDTO,
    ) -> UpdateUserCredentialsUseCaseOutputDTO:
        raise NotImplementedError
