import logging

from app.app_layer.interfaces.http.ssau.interface import SSAUProfileProvider
from app.domain.entities.ssau_profile import SsauProfile
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.subgroup import Subgroup
from app.domain.value_objects.year_id import YearId
from app.app_layer.interfaces.http.ssau.dto.profile import GroupDto, UnifiedYearDto
from app.infra.clients.ssau.ssau_client import SSAUClient

logger = logging.getLogger(__name__)


class SSAUProfileHttpProvider(SSAUProfileProvider):
    _GROUPS_PATH = "/api/proxy/personal/groups"
    _DICTIONARIES_PATH = "/api/proxy/dictionaries"
    _DICTIONARIES_SLUG = "unified_years"

    def __init__(
        self,
        client: SSAUClient,
    ) -> None:
        self._client = client
        self._groups_path = self._GROUPS_PATH
        self._dictionaries_path = self._DICTIONARIES_PATH
        self._dictionaries_slug = self._DICTIONARIES_SLUG

    async def fetch_profile(self, login: str, password: str) -> SsauProfile:
        groups = await self._fetch_groups(login, password)
        if not groups:
            raise RuntimeError("SSAU groups list is empty.")
        group = groups[0]

        years = await self._fetch_years(login, password)
        if not years:
            raise RuntimeError("SSAU years list is empty.")
        year = self._select_year(years)

        logger.info(
            "SSAU profile loaded: group=%s year=%s start=%s",
            group.id,
            year.id,
            year.start_date,
        )

        return SsauProfile(
            group_id=GroupId(value=group.id),
            group_name=group.name,
            year_id=YearId(value=year.id),
            academic_year_start=year.start_date,
            subgroup=Subgroup(value=1),
            user_type="student",
        )

    async def _fetch_groups(self, login: str, password: str) -> list[GroupDto]:
        response = await self._client.get(
            login=login,
            password=password,
            path=self._groups_path,
        )
        response.raise_for_status()
        data = response.json()
        return [GroupDto.model_validate(item) for item in data]

    async def _fetch_years(self, login: str, password: str) -> list[UnifiedYearDto]:
        response = await self._client.get(
            login=login,
            password=password,
            path=self._dictionaries_path,
            params={"slug": self._dictionaries_slug},
        )
        response.raise_for_status()
        data = response.json()
        return [UnifiedYearDto.model_validate(item) for item in data]

    @staticmethod
    def _select_year(years: list[UnifiedYearDto]) -> UnifiedYearDto:
        for item in years:
            if item.is_current:
                return item
        return years[-1]
