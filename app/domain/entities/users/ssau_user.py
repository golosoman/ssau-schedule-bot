from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.year_id import YearId


class SsauProfileIds(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    group_id: GroupId
    year_id: YearId


class SsauProfileDetails(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    group_name: str
    academic_year_start: date
    subgroup: Subgroup
    user_type: str


class SsauProfile(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    profile_ids: SsauProfileIds
    profile_details: SsauProfileDetails


class SsauCredentials(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    login: str
    password: str


class SsauUser(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    credentials: SsauCredentials | None
    profile: SsauProfile | None
