from app.infra.observability.metrics.interface import IMetricsService


class SsauHttpClientMetrics:
    """Мост между наблюдениями ``BaseHttpClient`` и метрикой SSAU в ``IMetricsService``."""

    def __init__(self, metrics: IMetricsService) -> None:
        self._metrics = metrics

    def observe_request(
        self,
        *,
        client: str,
        method: str,
        path: str,
        status_code: int,
        duration: float,
    ) -> None:
        self._metrics.observe_ssau_request(path, status_code, duration)
