from datetime import date

from app.domain.entities.base import TimestampedEntity
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.year_id import YearId


class SsauProfileEntity(TimestampedEntity):
    """Профиль СНИУ (группа/год/подгруппа), привязан к SSAU-идентичности.

    Наличие сущности = профиль синхронизирован; ссылается на ``ssau_identity_id``.
    """

    ssau_identity_id: int
    group_id: GroupId
    year_id: YearId
    group_name: str
    academic_year_start: date
    subgroup: Subgroup
    user_type: str
