from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.check_telegram_chats.dto.input import (
    CheckTelegramChatsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.check_telegram_chats.dto.output import (
    CheckTelegramChatsUseCaseOutputDTO,
)


class ICheckTelegramChatsUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: CheckTelegramChatsUseCaseInputDTO,
    ) -> CheckTelegramChatsUseCaseOutputDTO:
        raise NotImplementedError

