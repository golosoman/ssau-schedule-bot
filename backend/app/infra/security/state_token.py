import base64
import binascii
import hashlib
import hmac

from app.app_layer.interfaces.security.state_token.errors import (
    ExpiredStateTokenError,
    InvalidStateTokenError,
)
from app.app_layer.interfaces.security.state_token.interface import IStateTokenService
from app.app_layer.interfaces.time.clock.interface import IClock


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


class HmacStateTokenService(IStateTokenService):
    """HMAC-SHA256 токен: payload ``chat_id:expiry`` + подпись. Формат ``<payload>.<sig>``
    (оба сегмента — base64url). Без хранения состояния: валидность проверяется подписью и TTL."""

    def __init__(self, secret: str, ttl_seconds: int, clock: IClock) -> None:
        self._secret = secret.encode("utf-8")
        self._ttl_seconds = ttl_seconds
        self._clock = clock

    def issue(self, chat_id: int) -> str:
        expiry = self._now() + self._ttl_seconds
        payload = f"{chat_id}:{expiry}".encode()
        return f"{_b64encode(payload)}.{_b64encode(self._sign(payload))}"

    def verify(self, token: str) -> int:
        try:
            payload_b64, signature_b64 = token.split(".", 1)
            payload = _b64decode(payload_b64)
            signature = _b64decode(signature_b64)
        except (ValueError, binascii.Error) as exc:
            raise InvalidStateTokenError("Malformed state token.") from exc

        if not hmac.compare_digest(self._sign(payload), signature):
            raise InvalidStateTokenError("Bad state token signature.")

        try:
            chat_id_raw, expiry_raw = payload.decode("utf-8").split(":", 1)
            chat_id = int(chat_id_raw)
            expiry = int(expiry_raw)
        except (ValueError, UnicodeDecodeError) as exc:
            raise InvalidStateTokenError("Bad state token payload.") from exc

        if self._now() >= expiry:
            raise ExpiredStateTokenError("State token expired.")
        return chat_id

    def _sign(self, payload: bytes) -> bytes:
        return hmac.new(self._secret, payload, hashlib.sha256).digest()

    def _now(self) -> int:
        return int(self._clock.now().timestamp())
