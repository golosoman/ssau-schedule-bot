import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.app_layer.interfaces.time.clock.interface import IClock
from app.infra.clients.ssau.settings import AuthCacheSettings
from app.logging.config import get_logger

logger = get_logger(__name__)

LoginFunc = Callable[[str, str], Awaitable[str]]


@dataclass(frozen=True)
class AuthCacheEntry:
    auth_cookie: str
    expires_at: datetime


class AuthSessionCache:
    """In-memory SSAU auth-cookie cache with per-login refresh throttling."""

    def __init__(
        self,
        *,
        settings: AuthCacheSettings,
        clock: IClock,
    ) -> None:
        self._settings = settings
        self._clock = clock
        self._lock = asyncio.Lock()
        self._entries: dict[str, AuthCacheEntry] = {}
        self._last_login_at: dict[str, datetime] = {}

    async def get_or_refresh(
        self,
        login: str,
        password: str,
        login_func: LoginFunc,
    ) -> str:
        now = self._clock.now()
        entry = self._entries.get(login)
        if entry and entry.expires_at > now:
            return entry.auth_cookie

        await self._respect_rate_limit(login, now)
        async with self._lock:
            entry = self._entries.get(login)
            if entry and entry.expires_at > self._clock.now():
                return entry.auth_cookie

            self._last_login_at[login] = self._clock.now()
            cookie = await login_func(login, password)
            expires_at = self._clock.now() + timedelta(seconds=self._settings.ttl_seconds)
            self._entries[login] = AuthCacheEntry(
                auth_cookie=cookie,
                expires_at=expires_at,
            )
            return cookie

    def invalidate(self, login: str) -> None:
        self._entries.pop(login, None)

    async def _respect_rate_limit(self, login: str, now: datetime) -> None:
        last_login = self._last_login_at.get(login)
        if last_login is None:
            return
        min_login_interval = timedelta(seconds=self._settings.min_login_interval_seconds)
        elapsed = now - last_login
        if elapsed >= min_login_interval:
            return
        wait_for = (min_login_interval - elapsed).total_seconds()
        logger.info("SSAU login throttled for %.2fs", wait_for)
        await asyncio.sleep(wait_for)
