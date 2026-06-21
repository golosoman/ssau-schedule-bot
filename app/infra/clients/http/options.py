from dataclasses import dataclass
from typing import Protocol

from app.infra.retry import RetryPolicy

DEFAULT_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


class HttpClientMetrics(Protocol):
    def observe_request(
        self,
        *,
        client: str,
        method: str,
        path: str,
        status_code: int,
        duration: float,
    ) -> None:
        raise NotImplementedError


class NoopHttpClientMetrics:
    def observe_request(
        self,
        *,
        client: str,
        method: str,
        path: str,
        status_code: int,
        duration: float,
    ) -> None:
        return None


@dataclass(frozen=True)
class BaseHttpClientOption:
    """Marker base for declarative ``BaseHttpClient`` options."""


@dataclass(frozen=True)
class WithMetrics(BaseHttpClientOption):
    metrics: HttpClientMetrics


@dataclass(frozen=True)
class WithRetry(BaseHttpClientOption):
    policy: RetryPolicy
    status_codes: frozenset[int] = DEFAULT_RETRY_STATUSES
