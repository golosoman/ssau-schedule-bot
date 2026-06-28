import logging

from app.logging.context import LoggingContext, get_request_id
from app.logging.redaction import redact_string

try:
    from opentelemetry import trace as otel_trace
except ModuleNotFoundError:
    otel_trace = None  # type: ignore[assignment]

RESERVED_LOG_RECORD_ATTRS = frozenset(logging.makeLogRecord({}).__dict__) | {
    "asctime",
    "message",
}


class LoggingContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        record.trace_id = _get_trace_id()
        for key, value in LoggingContext().items():
            if key not in RESERVED_LOG_RECORD_ATTRS:
                setattr(record, key, value)
        return True


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        redacted = redact_string(message)
        if redacted != message:
            record.msg = redacted
            record.args = ()
        return True


class SQLAlchemyErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        detail_index = message.find("DETAIL:")
        if detail_index == -1:
            return True

        newline_before_detail = message.rfind("\n", 0, detail_index)
        cutoff_point = detail_index if newline_before_detail == -1 else newline_before_detail
        record.msg = message[:cutoff_point] + "\n[REDACTED]"
        record.args = ()
        return True


def _get_trace_id() -> str | None:
    if otel_trace is None:
        return None

    span = otel_trace.get_current_span()
    context = span.get_span_context()
    if context and context.is_valid:
        return f"{context.trace_id:032x}"
    return None
