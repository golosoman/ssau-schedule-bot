from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.year_id import YearId


class FetchedSsauProfile(BaseModel):
    """Профиль из СГАУ (до персистентности). Подгруппу пользователь задаёт отдельно."""

    model_config = ConfigDict(frozen=True)

    group_id: GroupId
    year_id: YearId
    group_name: str
    academic_year_start: date
    user_type: str
