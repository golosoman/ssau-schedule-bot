from dependency_injector import containers, providers

from app.app_layer.interfaces.security.password_cipher.interface import IPasswordCipher
from app.app_layer.interfaces.time.clock.interface import IClock
from app.domain.value_objects.timezone import Timezone
from app.infra.security.password_cipher import (
    FernetPasswordCipher,
    PlaintextPasswordCipher,
)
from app.infra.time.system_clock import SystemClock
from app.settings.config import settings


def _password_cipher() -> IPasswordCipher:
    fernet_key = settings.security.fernet_key
    if fernet_key is not None:
        return FernetPasswordCipher(fernet_key.get_secret_value())
    return PlaintextPasswordCipher()


class CoreContainer(containers.DeclarativeContainer):
    clock: providers.Provider[IClock] = providers.Singleton(SystemClock)
    default_timezone: providers.Provider[Timezone] = providers.Singleton(
        Timezone,
        value=settings.notifications.default_timezone,
    )
    password_cipher: providers.Provider[IPasswordCipher] = providers.Singleton(_password_cipher)
