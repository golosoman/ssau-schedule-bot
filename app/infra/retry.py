from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt
from tenacity.wait import wait_combine, wait_exponential, wait_random

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay: float = 0.5
    max_delay: float = 5.0
    jitter: float = 0.2


class RetryableError(Exception):
    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    policy: RetryPolicy,
    is_retryable: Callable[[Exception], bool],
    on_retry: Callable[[Exception, float, int], None] | None = None,
) -> T:
    wait_strategy = _RetryAfterWait(_build_wait(policy))
    retrying = AsyncRetrying(
        retry=retry_if_exception(is_retryable),
        wait=wait_strategy,
        stop=stop_after_attempt(policy.max_attempts),
        reraise=True,
        before_sleep=_build_before_sleep(on_retry) if on_retry else None,
    )
    async for attempt in retrying:
        with attempt:
            return await operation()
    raise RuntimeError("Retrying failed without result.")


def _build_wait(policy: RetryPolicy):
    wait_strategy = wait_exponential(
        multiplier=policy.base_delay,
        max=policy.max_delay,
    )
    if policy.jitter > 0:
        wait_strategy = wait_combine(wait_strategy, wait_random(0, policy.jitter))
    return wait_strategy


def _build_before_sleep(on_retry: Callable[[Exception, float, int], None]):
    def _before_sleep(retry_state) -> None:
        if retry_state.outcome is None:
            return
        exc = retry_state.outcome.exception()
        delay = retry_state.next_action.sleep if retry_state.next_action else 0.0
        on_retry(exc, delay, retry_state.attempt_number)

    return _before_sleep


class _RetryAfterWait:
    def __init__(self, fallback) -> None:
        self._fallback = fallback

    def __call__(self, retry_state) -> float:
        if retry_state.outcome is None:
            return self._fallback(retry_state)
        exc = retry_state.outcome.exception()
        retry_after = getattr(exc, "retry_after", None)
        if retry_after is not None:
            return float(retry_after)
        return self._fallback(retry_state)
