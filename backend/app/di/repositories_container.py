from dependency_injector import containers, providers

from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.repos.notification_log.interface import (
    INotificationLogRepository,
)
from app.app_layer.interfaces.security.password_cipher.interface import IPasswordCipher
from app.infra.repos.account.repo import SqlAlchemyAccountRepository
from app.infra.repos.notification_log_repository import SqlAlchemyNotificationLogRepository


class RepositoriesContainer(containers.DeclarativeContainer):
    password_cipher: providers.Dependency[IPasswordCipher] = providers.Dependency()

    account_repo: providers.Provider[IAccountRepository] = providers.Singleton(
        SqlAlchemyAccountRepository,
        password_cipher=password_cipher,
    )
    notification_log_repo: providers.Provider[INotificationLogRepository] = providers.Singleton(
        SqlAlchemyNotificationLogRepository,
    )
