from __future__ import annotations

from datetime import time

from pydantic import BaseModel, ConfigDict, Field


class BaseDto(BaseModel):
    model_config = ConfigDict(extra="ignore")


class TeacherDto(BaseDto):
    name: str


class DisciplineDto(BaseDto):
    name: str


class WeekdayDto(BaseDto):
    id: int


class WeekDto(BaseDto):
    week: int
    is_online: bool = Field(default=False, alias="isOnline")


class TimeBlockDto(BaseDto):
    begin_time: time = Field(alias="beginTime")
    end_time: time = Field(alias="endTime")


class ConferenceDto(BaseDto):
    url: str | None = None


class GroupDto(BaseDto):
    subgroup: int | None = None


class LessonDto(BaseDto):
    id: int
    discipline: DisciplineDto
    teachers: list[TeacherDto] = Field(default_factory=list)
    weekday: WeekdayDto
    weeks: list[WeekDto] = Field(default_factory=list)
    time: TimeBlockDto
    conference: ConferenceDto | None = None
    groups: list[GroupDto] = Field(default_factory=list)
    weekly_detail: bool = Field(default=False, alias="weeklyDetail")


class ScheduleResponseDto(BaseDto):
    lessons: list[LessonDto] = Field(default_factory=list)
