import time

from prometheus_client import Counter, Histogram, start_http_server

SSAU_REQUESTS = Counter(
    "ssau_requests_total",
    "SSAU HTTP requests",
    ["path", "status"],
)
SSAU_REQUEST_DURATION = Histogram(
    "ssau_request_duration_seconds",
    "SSAU HTTP request duration",
    ["path"],
)
TELEGRAM_SENDS = Counter(
    "telegram_messages_total",
    "Telegram send attempts",
    ["status"],
)
WORKER_ERRORS = Counter(
    "worker_errors_total",
    "Worker loop errors",
    ["loop"],
)
SCHEDULE_SYNC_TOTAL = Counter(
    "schedule_sync_total",
    "Schedule sync attempts",
    ["status"],
)
NOTIFICATIONS_SENT = Counter(
    "notifications_sent_total",
    "Notifications sent",
    ["status"],
)


def start_metrics_server(host: str, port: int) -> None:
    start_http_server(port, addr=host)


def observe_ssau_request(path: str, status: int, duration: float) -> None:
    SSAU_REQUESTS.labels(path=path, status=str(status)).inc()
    SSAU_REQUEST_DURATION.labels(path=path).observe(duration)


def observe_telegram_send(status: str) -> None:
    TELEGRAM_SENDS.labels(status=status).inc()
    NOTIFICATIONS_SENT.labels(status=status).inc()


def observe_schedule_sync(status: str) -> None:
    SCHEDULE_SYNC_TOTAL.labels(status=status).inc()


def observe_worker_error(loop_name: str) -> None:
    WORKER_ERRORS.labels(loop=loop_name).inc()


class RequestTimer:
    def __init__(self) -> None:
        self._start = time.monotonic()

    def elapsed(self) -> float:
        return time.monotonic() - self._start
