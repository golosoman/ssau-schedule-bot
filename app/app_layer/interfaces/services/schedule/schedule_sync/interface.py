from __future__ import annotations

from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.schedule.schedule_sync.dto.input import (
    ScheduleSyncForUserInputDTO,
    ScheduleSyncIfStaleInputDTO,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.dto.output import (
    ScheduleSyncForUserOutputDTO,
    ScheduleSyncIfStaleOutputDTO,
)


class IScheduleSyncService(ABC):
    @abstractmethod
    async def sync_for_user(
        self,
        input_dto: ScheduleSyncForUserInputDTO,
    ) -> ScheduleSyncForUserOutputDTO:
        raise NotImplementedError

    @abstractmethod
    async def sync_if_stale(
        self,
        input_dto: ScheduleSyncIfStaleInputDTO,
    ) -> ScheduleSyncIfStaleOutputDTO:
        raise NotImplementedError
