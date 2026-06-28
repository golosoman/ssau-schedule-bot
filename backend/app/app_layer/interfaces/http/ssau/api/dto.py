from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field

from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.year_id import YearId


class FetchedSsauProfileDTO(BaseModel):
    """Профиль из СНИУ (до персистентности). Подгруппу пользователь задаёт отдельно."""

    model_config = ConfigDict(frozen=True)

    group_id: GroupId
    year_id: YearId
    group_name: str
    academic_year_start: date
    user_type: str


class BaseSsauDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")


class GroupDTO(BaseSsauDTO):
    id: int
    name: str


class UnifiedYearDTO(BaseSsauDTO):
    id: int
    year: int
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    weeks: int
    is_current: bool = Field(alias="isCurrent")
    is_elongated: bool = Field(alias="isElongated")


class TeacherDTO(BaseSsauDTO):
    name: str


class DisciplineDTO(BaseSsauDTO):
    name: str


class LessonTypeDTO(BaseSsauDTO):
    id: int
    name: str


class WeekdayDTO(BaseSsauDTO):
    id: int


class WeekDTO(BaseSsauDTO):
    week: int
    is_online: bool = Field(default=False, alias="isOnline")


class TimeBlockDTO(BaseSsauDTO):
    begin_time: time = Field(alias="beginTime")
    end_time: time = Field(alias="endTime")


class ConferenceDTO(BaseSsauDTO):
    url: str | None = None


class LessonGroupDTO(BaseSsauDTO):
    subgroup: int | None = None


class LessonDTO(BaseSsauDTO):
    id: int
    type: LessonTypeDTO
    discipline: DisciplineDTO
    teachers: list[TeacherDTO] = Field(default_factory=list)
    weekday: WeekdayDTO
    weeks: list[WeekDTO] = Field(default_factory=list)
    time: TimeBlockDTO
    conference: ConferenceDTO | None = None
    groups: list[LessonGroupDTO] = Field(default_factory=list)
    weekly_detail: bool = Field(default=False, alias="weeklyDetail")


class ScheduleResponseDTO(BaseSsauDTO):
    lessons: list[LessonDTO] = Field(default_factory=list)
