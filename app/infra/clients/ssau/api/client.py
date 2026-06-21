from typing import Any

import httpx

from app.app_layer.interfaces.http.ssau.api.dto.fetched import FetchedSsauProfile
from app.app_layer.interfaces.http.ssau.api.dto.profile import GroupDto, UnifiedYearDto
from app.app_layer.interfaces.http.ssau.api.dto.schedule import ScheduleResponseDto
from app.app_layer.interfaces.http.ssau.api.interface import ISsauApiClient
from app.app_layer.interfaces.http.ssau.auth.interface import ISsauAuthClient
from app.domain.constants import DEFAULT_USER_TYPE
from app.domain.entities.lesson import Lesson
from app.domain.value_objects.group_id import GroupId
from app.domain.value_objects.year_id import YearId
from app.infra.clients.http.client import BaseHttpClient
from app.infra.clients.http.options import BaseHttpClientOption, WithMetrics, WithRetry
from app.infra.clients.ssau.api.mapper import map_schedule
from app.infra.clients.ssau.api.session_cache import AuthSessionCache
from app.infra.clients.ssau.auth.client import ssau_default_headers
from app.infra.clients.ssau.metrics import SsauHttpClientMetrics
from app.infra.clients.ssau.settings import SSAUClientSettings
from app.infra.observability.metrics.interface import IMetricsService
from app.infra.retry import RetryPolicy
from app.logging.config import get_logger

logger = get_logger(__name__)


class SsauApiClient(BaseHttpClient, ISsauApiClient):
    """Authenticated SSAU data API: schedule + personal profile (groups/years).

    All endpoints are simple authenticated GETs against the same host, so they
    live on one client. Auth cookies are cached per login and refreshed on
    expiry; a 401/403 triggers a single re-login retry.
    """

    _SCHEDULE_PATH = "/api/proxy/timetable/get-timetable"
    _GROUPS_PATH = "/api/proxy/personal/groups"
    _DICTIONARIES_PATH = "/api/proxy/dictionaries"
    _DICTIONARIES_SLUG = "unified_years"

    def __init__(
        self,
        *,
        settings: SSAUClientSettings,
        auth_client: ISsauAuthClient,
        auth_cache: AuthSessionCache,
        retry_policy: RetryPolicy,
        metrics_service: IMetricsService | None = None,
    ) -> None:
        options: list[BaseHttpClientOption] = [WithRetry(retry_policy)]
        if metrics_service is not None:
            options.append(WithMetrics(SsauHttpClientMetrics(metrics_service)))
        super().__init__(
            "ssau",
            settings.base_url,
            *options,
            timeout_seconds=settings.timeout_seconds,
            default_headers=ssau_default_headers(settings.base_url),
        )
        self._settings = settings
        self._auth_client = auth_client
        self._auth_cache = auth_cache

    # --- ISsauApiClient: schedule ---

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
        logger.info(
            "Fetching schedule: week=%s group=%s year=%s",
            week_number,
            group_id,
            year_id,
        )
        response = await self._get_authenticated(
            login=login,
            password=password,
            path=self._SCHEDULE_PATH,
            params={
                "yearId": year_id,
                "week": week_number,
                "userType": user_type,
                "groupId": group_id,
            },
        )
        response.raise_for_status()
        data = ScheduleResponseDto.model_validate(response.json())
        return map_schedule(data)

    # --- ISsauApiClient: profile ---

    async def fetch_profile(self, login: str, password: str) -> FetchedSsauProfile:
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

        return FetchedSsauProfile(
            group_id=GroupId(value=group.id),
            year_id=YearId(value=year.id),
            group_name=group.name,
            academic_year_start=year.start_date,
            user_type=DEFAULT_USER_TYPE,
        )

    async def _fetch_groups(self, login: str, password: str) -> list[GroupDto]:
        response = await self._get_authenticated(
            login=login,
            password=password,
            path=self._GROUPS_PATH,
        )
        response.raise_for_status()
        data = response.json()
        return [GroupDto.model_validate(item) for item in data]

    async def _fetch_years(self, login: str, password: str) -> list[UnifiedYearDto]:
        response = await self._get_authenticated(
            login=login,
            password=password,
            path=self._DICTIONARIES_PATH,
            params={"slug": self._DICTIONARIES_SLUG},
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

    # --- authenticated transport ---

    async def _get_authenticated(
        self,
        *,
        login: str,
        password: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        cookie = await self._auth_cache.get_or_refresh(login, password, self._login)
        response = await self._send_authenticated("GET", path, cookie, params=params)
        if response.status_code not in {401, 403}:
            return response

        await response.aclose()
        logger.info("SSAU auth expired, re-login.")
        self._auth_cache.invalidate(login)
        cookie = await self._auth_cache.get_or_refresh(login, password, self._login)
        return await self._send_authenticated("GET", path, cookie, params=params)

    async def _send_authenticated(
        self,
        method: str,
        path: str,
        auth_cookie: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        try:
            return await self.request(
                method,
                path,
                params=params,
                cookies={"auth": auth_cookie},
            )
        finally:
            self.clear_cookies()

    async def _login(self, login: str, password: str) -> str:
        session = await self._auth_client.login(login, password)
        return session.auth_cookie
