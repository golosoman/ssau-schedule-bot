import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import httpx

from app.app_layer.interfaces.time.clock.interface import Clock
from app.infra.clients.http_client import HttpClientFactory
from app.infra.clients.ssau.auth_client import AuthClient
from app.infra.observability.metrics import (
    RequestTimer,
    observe_ssau_request,
)
from app.infra.observability.telemetry import get_tracer
from app.infra.retry import RetryPolicy, RetryableError, retry_async

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthCacheEntry:
    auth_cookie: str
    expires_at: datetime


class AuthSessionCache:
    def __init__(
        self,
        *,
        ttl_seconds: int,
        min_login_interval_seconds: int,
        clock: Clock,
    ) -> None:
        self._ttl = timedelta(seconds=ttl_seconds)
        self._min_login_interval = timedelta(seconds=min_login_interval_seconds)
        self._clock = clock
        self._lock = asyncio.Lock()
        self._entries: dict[str, AuthCacheEntry] = {}
        self._last_login_at: dict[str, datetime] = {}

    async def get_or_refresh(
        self,
        login: str,
        password: str,
        login_func,
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
            expires_at = self._clock.now() + self._ttl
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
        elapsed = now - last_login
        if elapsed >= self._min_login_interval:
            return
        wait_for = (self._min_login_interval - elapsed).total_seconds()
        logger.info("SSAU login throttled for %.2fs", wait_for)
        await asyncio.sleep(wait_for)


class SSAUClient:
    def __init__(
        self,
        *,
        base_url: str,
        auth_cache: AuthSessionCache,
        retry_policy: RetryPolicy,
        timeout_seconds: float,
    ) -> None:
        self._base_url = base_url
        self._auth_cache = auth_cache
        self._retry_policy = retry_policy
        self._timeout_seconds = timeout_seconds

    async def get(
        self,
        *,
        login: str,
        password: str,
        path: str,
        params: dict | None = None,
    ) -> httpx.Response:
        return await self._request(
            method="GET",
            login=login,
            password=password,
            path=path,
            params=params,
        )

    async def _request(
        self,
        *,
        method: str,
        login: str,
        password: str,
        path: str,
        params: dict | None = None,
    ) -> httpx.Response:
        async with HttpClientFactory.create(
            self._base_url,
            AuthClient._LOGIN_PATH,
            timeout_seconds=self._timeout_seconds,
        ) as client:
            cookie = await self._auth_cache.get_or_refresh(
                login,
                password,
                self._login,
            )
            client.cookies.set("auth", cookie)

            response = await self._send_with_retry(client, method, path, params=params)
            if response.status_code in {401, 403}:
                logger.info("SSAU auth expired, re-login.")
                self._auth_cache.invalidate(login)
                cookie = await self._auth_cache.get_or_refresh(
                    login,
                    password,
                    self._login,
                )
                client.cookies.set("auth", cookie)
                response = await self._send_with_retry(
                    client,
                    method,
                    path,
                    params=params,
                )

            return response

    async def _send_with_retry(
        self,
        client: httpx.AsyncClient,
        method: str,
        path: str,
        *,
        params: dict | None = None,
    ) -> httpx.Response:
        tracer = get_tracer(__name__)

        async def _operation() -> httpx.Response:
            timer = RequestTimer()
            with tracer.start_as_current_span("ssau.request") as span:
                span.set_attribute("http.method", method)
                span.set_attribute("http.target", path)
                response = await client.request(method, path, params=params)
                span.set_attribute("http.status_code", response.status_code)
            observe_ssau_request(path, response.status_code, timer.elapsed())
            if response.status_code in {429, 500, 502, 503, 504}:
                retry_after = _parse_retry_after(response)
                raise RetryableError(
                    f"SSAU retryable status: {response.status_code}",
                    retry_after=retry_after,
                )
            return response

        def _on_retry(exc: Exception, delay: float, attempt: int) -> None:
            logger.warning("SSAU retry %s in %.2fs (%s)", attempt, delay, exc)

        return await retry_async(
            _operation,
            policy=self._retry_policy,
            is_retryable=lambda exc: isinstance(exc, (httpx.RequestError, RetryableError)),
            on_retry=_on_retry,
        )

    async def _login(self, login: str, password: str) -> str:
        async with HttpClientFactory.create(
            self._base_url,
            AuthClient._LOGIN_PATH,
            timeout_seconds=self._timeout_seconds,
        ) as client:
            auth_client = AuthClient(client)
            session = await auth_client.login(login, password)
            return session.auth_cookie


def _parse_retry_after(response: httpx.Response) -> float | None:
    retry_after = response.headers.get("Retry-After")
    if retry_after is None:
        return None
    try:
        return float(retry_after)
    except ValueError:
        return None
