import logging

from app.domain.entities.lesson import Lesson
from app.domain.entities.user import User
from app.app_layer.interfaces.http.ssau.interface import ScheduleProvider
from app.app_layer.interfaces.http.ssau.dto.schedule import ScheduleResponseDto
from app.infra.clients.ssau.ssau_client import SSAUClient
from app.infra.clients.ssau.ssau_schedule_mapper import map_schedule

logger = logging.getLogger(__name__)


class SSAUScheduleProvider(ScheduleProvider):
    _SCHEDULE_PATH = "/api/proxy/timetable/get-timetable"

    def __init__(self, client: SSAUClient) -> None:
        self._client = client
        self._schedule_path = self._SCHEDULE_PATH

    async def fetch_week_schedule(self, user: User, week_number: int) -> list[Lesson]:
        if user.ssau.credentials is None:
            raise ValueError("User credentials are required to fetch schedule.")
        if user.ssau.profile is None:
            raise ValueError("User group/year is required to fetch schedule.")

        logger.info(
            "Fetching schedule: user=%s week=%s group=%s year=%s",
            user.telegram.chat_id,
            week_number,
            user.ssau.profile.group_id.value,
            user.ssau.profile.year_id.value,
        )
        response = await self._client.get(
            login=user.ssau.credentials.login,
            password=user.ssau.credentials.password,
            path=self._schedule_path,
            params={
                "yearId": user.ssau.profile.year_id.value,
                "week": week_number,
                "userType": user.ssau.profile.user_type,
                "groupId": user.ssau.profile.group_id.value,
            },
        )
        response.raise_for_status()
        data = ScheduleResponseDto.model_validate(response.json())
        return map_schedule(data)
