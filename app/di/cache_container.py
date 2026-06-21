from dependency_injector import containers, providers

from app.app_layer.interfaces.cache.interface import ICacheClient
from app.app_layer.interfaces.cache.schedule.interface import IScheduleCacheStore
from app.infra.cache.valkey.client import ValkeyClient, build_valkey_client
from app.infra.cache.valkey.schedule_cache import ValkeyScheduleCacheStore
from app.infra.cache.valkey.settings import ValkeyClientSettings
from app.settings.config import settings


def _valkey_password() -> str | None:
    password = settings.valkey.password
    return password.get_secret_value() if password is not None else None


class CacheContainer(containers.DeclarativeContainer):
    valkey_engine = providers.Resource(
        build_valkey_client,
        settings=providers.Singleton(
            ValkeyClientSettings,
            host=settings.valkey.host,
            port=settings.valkey.port,
            db=settings.valkey.db,
            password=providers.Callable(_valkey_password),
            max_connections=settings.valkey.max_connections,
            socket_timeout_seconds=settings.valkey.socket_timeout_seconds,
            socket_connect_timeout_seconds=settings.valkey.socket_connect_timeout_seconds,
            health_check_interval_seconds=settings.valkey.health_check_interval_seconds,
            retries=settings.valkey.retries,
        ),
    )
    cache_client: providers.Provider[ICacheClient] = providers.Singleton(
        ValkeyClient,
        client=valkey_engine,
    )
    schedule_cache_store: providers.Provider[IScheduleCacheStore] = providers.Singleton(
        ValkeyScheduleCacheStore,
        client=cache_client,
        ttl_seconds=settings.workers.schedule_fetch_interval_hours * 3600,
    )
