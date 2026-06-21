from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.cache.schedule.dto import CachedWeek


class ScheduleSyncForUserOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    cache: CachedWeek


class ScheduleSyncIfStaleOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    cache: CachedWeek
