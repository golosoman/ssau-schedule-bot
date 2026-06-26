import inspect
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from dependency_injector import containers, providers

from app.di.cache_container import CacheContainer
from app.di.core_container import CoreContainer
from app.di.db_container import DbContainer
from app.di.metrics_container import MetricsContainer
from app.di.repositories_container import RepositoriesContainer
from app.di.services_container import ServicesContainer
from app.di.ssau_container import SsauContainer
from app.di.telegram_container import TelegramContainer
from app.di.usecases_container import UseCasesContainer


class Container(containers.DeclarativeContainer):
    core = providers.Container(CoreContainer)
    db = providers.Container(DbContainer)
    cache = providers.Container(CacheContainer)
    metrics = providers.Container(MetricsContainer)
    telegram = providers.Container(TelegramContainer, metrics=metrics)
    ssau = providers.Container(SsauContainer, clock=core.clock, metrics=metrics)
    repositories = providers.Container(
        RepositoriesContainer,
        password_cipher=core.password_cipher,
    )
    services = providers.Container(
        ServicesContainer,
        core=core,
        cache=cache,
        ssau=ssau,
        repositories=repositories,
        telegram=telegram,
    )
    usecases = providers.Container(
        UseCasesContainer,
        db=db,
        repositories=repositories,
        ssau=ssau,
        telegram=telegram,
        services=services,
    )


async def resolve_resource(provider: providers.Provider[Any]) -> Any:
    """Резолвит provider, дожидаясь async Resource при прямом обращении."""
    result = provider()
    return await result if inspect.isawaitable(result) else result


@asynccontextmanager
async def di_scope(
    wiring_params: dict[str, Any] | None = None,
) -> AsyncIterator[Container]:
    """Единственная точка lifecycle DI: создаёт контейнер, открывает все Resource
    на входе и закрывает их на выходе."""
    container = Container()
    if wiring_params:
        container.wire(**wiring_params)
    resources = container.init_resources()
    if resources is not None:
        await resources
    try:
        yield container
    finally:
        resources = container.shutdown_resources()
        if resources is not None:
            await resources
