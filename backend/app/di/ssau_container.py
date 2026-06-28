from dependency_injector import containers, providers

from app.app_layer.interfaces.http.ssau.api.interface import ISsauApiClient
from app.app_layer.interfaces.http.ssau.auth.interface import ISsauAuthClient
from app.app_layer.interfaces.time.clock.interface import IClock
from app.infra.clients.ssau.api.client import SsauApiClient
from app.infra.clients.ssau.api.session_cache import AuthSessionCache
from app.infra.clients.ssau.auth.client import SsauAuthClient
from app.infra.clients.ssau.settings import AuthCacheSettings, SSAUClientSettings
from app.infra.retry import RetryPolicy
from app.settings.config import settings


class SsauContainer(containers.DeclarativeContainer):
    clock: providers.Dependency[IClock] = providers.Dependency()
    metrics = providers.DependenciesContainer()

    retry_policy: providers.Provider[RetryPolicy] = providers.Singleton(
        RetryPolicy,
        max_attempts=settings.ssau.retry.max_attempts,
        base_delay=settings.ssau.retry.base_seconds,
        max_delay=settings.ssau.retry.max_seconds,
        jitter=settings.ssau.retry.jitter_seconds,
    )
    client_settings: providers.Provider[SSAUClientSettings] = providers.Singleton(
        SSAUClientSettings,
        base_url=settings.ssau.base_url,
        timeout_seconds=settings.ssau.retry.timeout_seconds,
    )
    auth_cache: providers.Provider[AuthSessionCache] = providers.Singleton(
        AuthSessionCache,
        settings=providers.Singleton(
            AuthCacheSettings,
            ttl_seconds=settings.ssau.auth.cookie_ttl_seconds,
            min_login_interval_seconds=settings.ssau.auth.min_login_interval_seconds,
        ),
        clock=clock,
    )
    auth_client: providers.Provider[ISsauAuthClient] = providers.Resource(
        SsauAuthClient,
        settings=client_settings,
        retry_policy=retry_policy,
        metrics_service=metrics.metrics_service,
    )
    # Один авторизованный data-клиент закрывает оба порта (schedule + profile).
    # SsauApiClient — async context manager, lifecycle ведёт сам providers.Resource.
    api_client: providers.Provider[ISsauApiClient] = providers.Resource(
        SsauApiClient,
        settings=client_settings,
        auth_client=auth_client,
        auth_cache=auth_cache,
        retry_policy=retry_policy,
        metrics_service=metrics.metrics_service,
    )
