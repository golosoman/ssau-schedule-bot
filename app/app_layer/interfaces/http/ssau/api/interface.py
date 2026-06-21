from abc import ABC, abstractmethod

from app.app_layer.interfaces.http.ssau.api.dto.fetched import FetchedSsauProfile
from app.domain.entities.lesson import Lesson


class ISsauApiClient(ABC):
    """Контракт SSAU data-клиента: расписание + персональный профиль."""

    @abstractmethod
    async def fetch_week_schedule(
        self,
        *,
        login: str,
        password: str,
        group_id: int,
        year_id: int,
        user_type: str,
        week_number: int,
    ) -> list[Lesson]:
        raise NotImplementedError

    @abstractmethod
    async def fetch_profile(self, login: str, password: str) -> FetchedSsauProfile:
        raise NotImplementedError
