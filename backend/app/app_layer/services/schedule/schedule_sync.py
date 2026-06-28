from datetime import date

from app.app_layer.interfaces.cache.schedule.dto import CachedWeekDTO
from app.app_layer.interfaces.cache.schedule.interface import IScheduleCacheStore
from app.app_layer.interfaces.http.ssau.api.interface import ISsauApiClient
from app.app_layer.interfaces.repos.account.dto import AccountViewDTO
from app.app_layer.interfaces.services.schedule.schedule_sync.dto import (
    ScheduleSyncForUserInputDTO,
    ScheduleSyncForUserOutputDTO,
    ScheduleSyncIfStaleInputDTO,
    ScheduleSyncIfStaleOutputDTO,
)
from app.app_layer.interfaces.services.schedule.schedule_sync.interface import (
    IScheduleSyncService,
)
from app.app_layer.interfaces.services.schedule.week_calculator.dto import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.app_layer.interfaces.time.clock.interface import IClock
from app.logging.config import get_logger

logger = get_logger(__name__)


class ScheduleSyncService(IScheduleSyncService):
    def __init__(
        self,
        provider: ISsauApiClient,
        clock: IClock,
        week_calculator: IWeekCalculatorService,
        cache_store: IScheduleCacheStore,
    ) -> None:
        self._provider = provider
        self._clock = clock
        self._week_calculator = week_calculator
        self._cache_store = cache_store

    async def sync_for_user(
        self,
        input_dto: ScheduleSyncForUserInputDTO,
    ) -> ScheduleSyncForUserOutputDTO:
        account = input_dto.account
        week_number = self._week_number(account, input_dto.target_date)
        cache = await self._fetch_and_store(account, week_number)
        return ScheduleSyncForUserOutputDTO(cache=cache)

    async def sync_if_stale(
        self,
        input_dto: ScheduleSyncIfStaleInputDTO,
    ) -> ScheduleSyncIfStaleOutputDTO:
        account = input_dto.account
        week_number = self._week_number(account, input_dto.target_date)
        cache = await self._cache_store.get(account.account_id, week_number)
        if cache is not None:
            return ScheduleSyncIfStaleOutputDTO(cache=cache)
        fresh = await self._fetch_and_store(account, week_number)
        return ScheduleSyncIfStaleOutputDTO(cache=fresh)

    def _week_number(self, account: AccountViewDTO, target_date: date) -> int:
        if account.ssau_profile is None:
            raise ValueError("User SSAU profile is required to sync schedule.")
        return self._week_calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=account.ssau_profile.academic_year_start,
                target_date=target_date,
            )
        ).week_number

    async def _fetch_and_store(self, account: AccountViewDTO, week_number: int) -> CachedWeekDTO:
        if account.ssau_identity is None or account.ssau_profile is None:
            raise ValueError("Credentials and SSAU profile are required to sync schedule.")
        lessons = await self._provider.fetch_week_schedule(
            login=account.ssau_identity.login,
            password=account.ssau_identity.password,
            group_id=account.ssau_profile.group_id.value,
            year_id=account.ssau_profile.year_id.value,
            user_type=account.ssau_profile.user_type,
            week_number=week_number,
        )
        cache = CachedWeekDTO(fetched_at=self._clock.now(), lessons=lessons)
        await self._cache_store.set(account.account_id, week_number, cache)
        return cache
