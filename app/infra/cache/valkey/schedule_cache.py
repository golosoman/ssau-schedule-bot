from app.app_layer.interfaces.cache.interface import ICacheClient
from app.app_layer.interfaces.cache.schedule.dto import CachedWeek
from app.app_layer.interfaces.cache.schedule.interface import IScheduleCacheStore


class ValkeyScheduleCacheStore(IScheduleCacheStore):
    """Кэш расписания в Valkey: ключ ``schedule:{account_id}:{week}`` → JSON ``CachedWeek``.

    Свежесть обеспечивает TTL Valkey (``SETEX``): вернулся ключ — он ещё актуален.
    """

    _KEY_PREFIX = "schedule"

    def __init__(self, client: ICacheClient, ttl_seconds: int) -> None:
        self._client = client
        self._ttl_seconds = ttl_seconds

    def _key(self, account_id: int, week_number: int) -> str:
        return f"{self._KEY_PREFIX}:{account_id}:{week_number}"

    async def get(self, account_id: int, week_number: int) -> CachedWeek | None:
        raw = await self._client.get(self._key(account_id, week_number))
        if raw is None:
            return None
        return CachedWeek.model_validate_json(raw)

    async def set(self, account_id: int, week_number: int, week: CachedWeek) -> None:
        await self._client.set(
            self._key(account_id, week_number),
            week.model_dump_json(),
            ttl=self._ttl_seconds,
        )
