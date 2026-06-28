from datetime import date

from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.cache.schedule.dto import CachedWeekDTO
from app.app_layer.interfaces.repos.account.dto import AccountViewDTO


class ScheduleSyncForUserInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO
    target_date: date


class ScheduleSyncIfStaleInputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    account: AccountViewDTO
    target_date: date


class ScheduleSyncForUserOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    cache: CachedWeekDTO


class ScheduleSyncIfStaleOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    cache: CachedWeekDTO
