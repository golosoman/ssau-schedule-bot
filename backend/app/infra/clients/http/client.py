import time
from collections.abc import Mapping
from types import TracebackType
from typing import Any, Self

import httpx

from app.infra.clients.http.errors import RetryableHttpStatusError
from app.infra.clients.http.options import (
    DEFAULT_RETRY_STATUSES,
    BaseHttpClientOption,
    HttpClientMetrics,
    NoopHttpClientMetrics,
    WithMetrics,
    WithRetry,
)
from app.infra.observability.telemetry.tracing import get_tracer
from app.infra.retry import RetryPolicy, retry_async
from app.logging.config import get_logger

logger = get_logger(__name__)


class BaseHttpClient:
    """Reusable async HTTP client over httpx.

    Instances are async context managers and should be registered in DI as
    resources. Concrete clients keep domain-specific methods and reuse
    ``request``/``send`` for lifecycle, retries and metrics.
    """

    def __init__(
        self,
        client_name: str,
        base_url: str,
        *options: BaseHttpClientOption,
        timeout_seconds: float = 15.0,
        default_headers: Mapping[str, str] | None = None,
        follow_redirects: bool = True,
    ) -> None:
        self._client_name = client_name
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._default_headers = dict(default_headers or {})
        self._follow_redirects = follow_redirects
        self._metrics: HttpClientMetrics = NoopHttpClientMetrics()
        self._retry_policy: RetryPolicy | None = None
        self._retry_status_codes: frozenset[int] = DEFAULT_RETRY_STATUSES
        self._session: httpx.AsyncClient | None = None
        self._apply_options(options)

    def _apply_options(self, options: tuple[BaseHttpClientOption, ...]) -> None:
        for option in options:
            if isinstance(option, WithMetrics):
                self._metrics = option.metrics
            elif isinstance(option, WithRetry):
                self._retry_policy = option.policy
                self._retry_status_codes = option.status_codes

    async def __aenter__(self) -> Self:
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(
                base_url=self._base_url,
                follow_redirects=self._follow_redirects,
                timeout=httpx.Timeout(self._timeout_seconds),
                headers=self._default_headers,
            )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None:
        if self._session is not None and not self._session.is_closed:
            await self._session.aclose()

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("POST", path, **kwargs)

    async def do(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        data: Any = None,
        json: Any = None,
        retry: bool = True,
    ) -> Any:
        """Perform a request and return parsed JSON, raising on HTTP error.

        Convenience for simple JSON APIs; clients that need response-level
        access (cookies, streaming) should use ``request``/``send`` instead.
        """
        response = await self.request(
            method,
            path,
            params=params,
            headers=headers,
            cookies=cookies,
            data=data,
            json=json,
            retry=retry,
        )
        response.raise_for_status()
        return response.json()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        data: Any = None,
        json: Any = None,
        files: Any = None,
        follow_redirects: bool | None = None,
        retry: bool = True,
    ) -> httpx.Response:
        should_retry = self._retry_policy is not None and retry

        async def _operation() -> httpx.Response:
            return await self._request_once(
                method,
                path,
                params=params,
                headers=headers,
                cookies=cookies,
                data=data,
                json=json,
                files=files,
                follow_redirects=follow_redirects,
                raise_retryable_status=should_retry,
            )

        if not should_retry:
            return await _operation()

        assert self._retry_policy is not None
        return await retry_async(
            _operation,
            policy=self._retry_policy,
            is_retryable=_is_retryable_http_error,
            on_retry=self._log_retry,
        )

    def build_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Request:
        return self._get_session().build_request(method, path, **kwargs)

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        follow_redirects: bool | None = None,
        retry: bool = False,
    ) -> httpx.Response:
        should_retry = self._retry_policy is not None and retry

        async def _operation() -> httpx.Response:
            return await self._send_once(
                request,
                stream=stream,
                follow_redirects=follow_redirects,
                raise_retryable_status=should_retry,
            )

        if not should_retry:
            return await _operation()

        assert self._retry_policy is not None
        return await retry_async(
            _operation,
            policy=self._retry_policy,
            is_retryable=_is_retryable_http_error,
            on_retry=self._log_retry,
        )

    def clear_cookies(self) -> None:
        if self._session is None or self._session.is_closed:
            return
        self._session.cookies.clear()

    async def _request_once(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None,
        headers: Mapping[str, str] | None,
        cookies: dict[str, str] | None,
        data: Any,
        json: Any,
        files: Any,
        follow_redirects: bool | None,
        raise_retryable_status: bool,
    ) -> httpx.Response:
        tracer = get_tracer(__name__)
        started = time.monotonic()
        status_code = 0
        try:
            with tracer.start_as_current_span("http.client.request") as span:
                span.set_attribute("http.client", self._client_name)
                span.set_attribute("http.method", method)
                span.set_attribute("http.target", path)
                request_kwargs: dict[str, Any] = {}
                if follow_redirects is not None:
                    request_kwargs["follow_redirects"] = follow_redirects
                response = await self._get_session().request(
                    method,
                    path,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    data=data,
                    json=json,
                    files=files,
                    **request_kwargs,
                )
                status_code = response.status_code
                span.set_attribute("http.status_code", status_code)
            if raise_retryable_status:
                await self._raise_for_retryable_status(response)
            return response
        finally:
            self._metrics.observe_request(
                client=self._client_name,
                method=method,
                path=path,
                status_code=status_code,
                duration=time.monotonic() - started,
            )

    async def _send_once(
        self,
        request: httpx.Request,
        *,
        stream: bool,
        follow_redirects: bool | None,
        raise_retryable_status: bool,
    ) -> httpx.Response:
        tracer = get_tracer(__name__)
        started = time.monotonic()
        status_code = 0
        path = request.url.path
        try:
            with tracer.start_as_current_span("http.client.send") as span:
                span.set_attribute("http.client", self._client_name)
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.target", path)
                send_kwargs: dict[str, Any] = {"stream": stream}
                if follow_redirects is not None:
                    send_kwargs["follow_redirects"] = follow_redirects
                response = await self._get_session().send(
                    request,
                    **send_kwargs,
                )
                status_code = response.status_code
                span.set_attribute("http.status_code", status_code)
            if raise_retryable_status:
                await self._raise_for_retryable_status(response)
            return response
        finally:
            self._metrics.observe_request(
                client=self._client_name,
                method=request.method,
                path=path,
                status_code=status_code,
                duration=time.monotonic() - started,
            )

    async def _raise_for_retryable_status(self, response: httpx.Response) -> None:
        if response.status_code not in self._retry_status_codes:
            return
        retry_after = _parse_retry_after(response)
        await response.aclose()
        raise RetryableHttpStatusError(response.status_code, retry_after)

    def _get_session(self) -> httpx.AsyncClient:
        if self._session is None or self._session.is_closed:
            raise RuntimeError(f"{self.__class__.__name__} session is not initialized.")
        return self._session

    def _log_retry(self, exc: Exception, delay: float, attempt: int) -> None:
        logger.warning(
            "%s retry %s in %.2fs (%s)",
            self.__class__.__name__,
            attempt,
            delay,
            exc,
        )


def _is_retryable_http_error(exc: Exception) -> bool:
    return isinstance(exc, (httpx.RequestError, RetryableHttpStatusError))


def _parse_retry_after(response: httpx.Response) -> float | None:
    retry_after = response.headers.get("Retry-After")
    if retry_after is None:
        return None
    try:
        return float(retry_after)
    except ValueError:
        return None
