from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.sync_user_profile.dto import (
    SyncUserProfileUseCaseInputDTO,
    SyncUserProfileUseCaseOutputDTO,
)


class ISyncUserProfileUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: SyncUserProfileUseCaseInputDTO,
    ) -> SyncUserProfileUseCaseOutputDTO:
        raise NotImplementedError
