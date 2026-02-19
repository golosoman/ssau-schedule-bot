import httpx

from app.app_layer.interfaces.http.ssau.dto.schedule import ScheduleResponseDto
from app.app_layer.interfaces.http.ssau.interface import ScheduleRepository
from app.domain.constants import DEFAULT_USER_TYPE
from app.domain.entities.lesson import Lesson
from app.infra.clients.ssau.ssau_schedule_mapper import map_schedule


class SSAUScheduleRepository(ScheduleRepository):
    _SCHEDULE_PATH = "/api/proxy/timetable/get-timetable"

    def __init__(
        self,
        client: httpx.AsyncClient,
        year_id: int,
        group_id: int,
        user_type: str = DEFAULT_USER_TYPE,
    ):
        self._client = client
        self._schedule_path = self._SCHEDULE_PATH
        self._year_id = year_id
        self._group_id = group_id
        self._user_type = user_type

    async def get_schedule(self, week: int) -> list[Lesson]:
        response = await self._client.get(
            self._schedule_path,
            params={
                "yearId": self._year_id,
                "week": week,
                "userType": self._user_type,
                "groupId": self._group_id,
            },
        )

        response.raise_for_status()
        data = ScheduleResponseDto.model_validate(response.json())

        return map_schedule(data)
