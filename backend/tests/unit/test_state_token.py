from datetime import UTC, datetime, timedelta

import pytest

from app.app_layer.interfaces.security.state_token.errors import (
    ExpiredStateTokenError,
    InvalidStateTokenError,
)
from app.infra.security.state_token import HmacStateTokenService

SECRET = "test-secret"


class _FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += timedelta(seconds=seconds)


def _service(clock: _FakeClock, *, secret: str = SECRET) -> HmacStateTokenService:
    return HmacStateTokenService(secret, ttl_seconds=900, clock=clock)


def _clock() -> _FakeClock:
    return _FakeClock(datetime(2026, 1, 1, tzinfo=UTC))


def test_issue_then_verify_roundtrips_chat_id() -> None:
    service = _service(_clock())
    token = service.issue(677532211)
    assert service.verify(token) == 677532211


def test_expired_token_rejected() -> None:
    clock = _clock()
    service = _service(clock)
    token = service.issue(42)
    clock.advance(901)
    with pytest.raises(ExpiredStateTokenError):
        service.verify(token)


def test_tampered_signature_rejected() -> None:
    service = _service(_clock())
    payload, signature = service.issue(42).split(".")
    forged = f"{payload}.{signature[:-2]}xx"
    with pytest.raises(InvalidStateTokenError):
        service.verify(forged)


def test_wrong_secret_rejected() -> None:
    clock = _clock()
    token = _service(clock, secret="secret-a").issue(42)
    with pytest.raises(InvalidStateTokenError):
        _service(clock, secret="secret-b").verify(token)


@pytest.mark.parametrize("bad", ["", "no-dot", "a.b.c", "!!!.???"])
def test_malformed_token_rejected(bad: str) -> None:
    with pytest.raises(InvalidStateTokenError):
        _service(_clock()).verify(bad)
