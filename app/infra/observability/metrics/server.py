from prometheus_client import start_http_server


def start_metrics_server(host: str, port: int) -> None:
    """Поднимает HTTP-эндпоинт Prometheus (глобальный REGISTRY) в фоновом потоке."""
    start_http_server(port, addr=host)
