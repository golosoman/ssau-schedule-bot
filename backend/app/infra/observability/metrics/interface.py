from abc import ABC, abstractmethod


class IMetricsService(ABC):
    """Контракт метрик приложения: типизированные доменные наблюдения."""

    @abstractmethod
    def observe_ssau_request(self, path: str, status: int, duration: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def observe_telegram_send(self, status: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def observe_schedule_sync(self, status: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def observe_worker_error(self, loop: str) -> None:
        raise NotImplementedError
