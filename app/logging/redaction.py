import re
from collections.abc import Mapping, Sequence
from typing import Any

REDACT_PATTERNS = (
    re.compile(r"(?i)(password|token|secret|auth_cookie|cookie)=([^\s]+)"),
)
SENSITIVE_KEYS = frozenset({"password", "token", "secret", "auth_cookie", "cookie", "api_key"})


def redact_string(value: str) -> str:
    redacted = value
    for pattern in REDACT_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}=***", redacted)
    return redacted


def redact_value(key: str, value: Any) -> Any:
    if _is_sensitive_key(key):
        return "***"
    if isinstance(value, str):
        return redact_string(value)
    if isinstance(value, Mapping):
        return {
            str(item_key): redact_value(str(item_key), item_value)
            for item_key, item_value in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [redact_value(key, item) for item in value]
    return value


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(part in normalized for part in SENSITIVE_KEYS)
