from pydantic import BaseModel, ConfigDict

from app.domain.entities.schedule_cache import ScheduleCache


class ScheduleSyncForUserOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    cache: ScheduleCache


class ScheduleSyncIfStaleOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    cache: ScheduleCache
