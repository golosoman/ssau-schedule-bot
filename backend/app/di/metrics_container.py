from dependency_injector import containers, providers

from app.infra.observability.metrics.interface import IMetricsService
from app.infra.observability.metrics.service import MetricsService


class MetricsContainer(containers.DeclarativeContainer):
    metrics_service: providers.Provider[IMetricsService] = providers.Singleton(MetricsService)
