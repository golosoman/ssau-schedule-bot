from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.sync_user_profile.dto.input import (
    SyncUserProfileUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.dto.output import (
    SyncUserProfileUseCaseOutputDTO,
)


class ISyncUserProfileUseCase(ABC):
    @abstractmethod
    async def execute(
        self,
        input_dto: SyncUserProfileUseCaseInputDTO,
    ) -> SyncUserProfileUseCaseOutputDTO:
        raise NotImplementedError
