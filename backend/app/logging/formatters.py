import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.logging.filters import RESERVED_LOG_RECORD_ATTRS
from app.logging.redaction import redact_value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "trace_id": getattr(record, "trace_id", None),
        }
        payload.update(_extra_payload(record))

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)

        return json.dumps(payload, ensure_ascii=True, default=str)


def _extra_payload(record: logging.LogRecord) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in record.__dict__.items():
        if key in RESERVED_LOG_RECORD_ATTRS or key in payload:
            continue
        if key in {"request_id", "trace_id"}:
            continue
        payload[key] = redact_value(key, value)
    return payload
