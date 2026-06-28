from prometheus_client import REGISTRY, CollectorRegistry, Counter, Histogram

from app.infra.observability.metrics.interface import IMetricsService


class MetricsService(IMetricsService):
    """Единая точка работы с метриками приложения: все Prometheus-объекты собраны
    здесь, наружу торчат только типизированные доменные методы (никаких сырых
    label-имён у вызывающего кода).

    Регистрируется как DI-singleton — метрики создаются один раз на процесс.
    ``registry`` можно подменить (напр. свежий ``CollectorRegistry`` в тестах),
    по умолчанию — глобальный, который и отдаёт ``start_metrics_server``.
    """

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        reg = registry if registry is not None else REGISTRY
        self._ssau_requests = Counter(
            "ssau_requests_total",
            "SSAU HTTP requests",
            ["path", "status"],
            registry=reg,
        )
        self._ssau_request_duration = Histogram(
            "ssau_request_duration_seconds",
            "SSAU HTTP request duration",
            ["path"],
            registry=reg,
        )
        self._telegram_sends = Counter(
            "telegram_messages_total",
            "Telegram send attempts",
            ["status"],
            registry=reg,
        )
        self._notifications_sent = Counter(
            "notifications_sent_total",
            "Notifications sent",
            ["status"],
            registry=reg,
        )
        self._worker_errors = Counter(
            "worker_errors_total",
            "Worker loop errors",
            ["loop"],
            registry=reg,
        )
        self._schedule_sync = Counter(
            "schedule_sync_total",
            "Schedule sync attempts",
            ["status"],
            registry=reg,
        )

    def observe_ssau_request(self, path: str, status: int, duration: float) -> None:
        self._ssau_requests.labels(path=path, status=str(status)).inc()
        self._ssau_request_duration.labels(path=path).observe(duration)

    def observe_telegram_send(self, status: str) -> None:
        self._telegram_sends.labels(status=status).inc()
        self._notifications_sent.labels(status=status).inc()

    def observe_schedule_sync(self, status: str) -> None:
        self._schedule_sync.labels(status=status).inc()

    def observe_worker_error(self, loop: str) -> None:
        self._worker_errors.labels(loop=loop).inc()
