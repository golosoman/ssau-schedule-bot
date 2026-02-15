from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.year_id import YearId


class SsauProfile(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    group_id: GroupId
    group_name: str
    year_id: YearId
    academic_year_start: date
    subgroup: Subgroup
    user_type: str
