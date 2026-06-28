from typing import Any

import valkey.asyncio as valkey
from valkey.asyncio.retry import Retry
from valkey.backoff import ExponentialBackoff

from app.app_layer.interfaces.cache.interface import ICacheClient
from app.infra.cache.valkey.settings import ValkeyClientSettings


def build_valkey_client(settings: ValkeyClientSettings) -> valkey.Valkey:
    """Собирает production-ready async-клиент Valkey.

    - встроенный пул соединений (``max_connections``);
    - повтор на сетевых ошибках с экспоненциальной паузой (``retry``);
    - keepalive + периодический health-check соединений;
    - ленивое подключение: первый запрос открывает соединение (старт без живого Valkey не падает).

    Ответы не декодируются (``decode_responses=False``) — кэш хранит JSON-байты.
    """
    return valkey.Valkey(
        host=settings.host,
        port=settings.port,
        db=settings.db,
        password=settings.password,
        max_connections=settings.max_connections,
        socket_timeout=settings.socket_timeout_seconds,
        socket_connect_timeout=settings.socket_connect_timeout_seconds,
        socket_keepalive=True,
        health_check_interval=settings.health_check_interval_seconds,
        retry=Retry(ExponentialBackoff(), settings.retries),
        decode_responses=False,
    )


class ValkeyClient(ICacheClient):
    def __init__(self, client: valkey.Valkey) -> None:
        self._client = client

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        *,
        nx: bool = False,
        get: bool = False,
    ) -> Any | None:
        return await self._client.set(
            name=key,
            value=value,
            ex=ttl,
            nx=nx,
            get=get,
        )

    async def get(self, key: str) -> Any | None:
        return await self._client.get(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))

    async def incr(self, key: str) -> int:
        return int(await self._client.incr(key))

    async def delete(self, key: str) -> int:
        return int(await self._client.delete(key))
