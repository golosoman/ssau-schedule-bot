from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.send_admin_message.dto import (
    SendAdminMessageUseCaseInputDTO,
    SendAdminMessageUseCaseOutputDTO,
)


class ISendAdminMessageUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: SendAdminMessageUseCaseInputDTO,
    ) -> SendAdminMessageUseCaseOutputDTO:
        raise NotImplementedError
