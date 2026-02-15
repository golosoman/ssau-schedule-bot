from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class BaseDto(BaseModel):
    model_config = ConfigDict(extra="ignore")


class GroupDto(BaseDto):
    id: int
    name: str


class UnifiedYearDto(BaseDto):
    id: int
    year: int
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    weeks: int
    is_current: bool = Field(alias="isCurrent")
    is_elongated: bool = Field(alias="isElongated")
