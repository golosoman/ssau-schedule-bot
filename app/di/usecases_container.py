from dependency_injector import containers, providers

from app.app_layer.interfaces.use_cases.check_telegram_chats.interface import (
    ICheckTelegramChatsUseCase,
)
from app.app_layer.interfaces.use_cases.list_accounts.interface import IListAccountsUseCase
from app.app_layer.interfaces.use_cases.register_user.interface import (
    IRegisterUserUseCase,
)
from app.app_layer.interfaces.use_cases.send_admin_message.interface import (
    ISendAdminMessageUseCase,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.interface import (
    IUpdateUserCredentialsUseCase,
)
from app.app_layer.interfaces.use_cases.update_user_settings.interface import (
    IUpdateUserSettingsUseCase,
)
from app.app_layer.use_cases.check_telegram_chats import CheckTelegramChatsUseCase
from app.app_layer.use_cases.list_accounts import ListAccountsUseCase
from app.app_layer.use_cases.register_user import RegisterUserUseCase
from app.app_layer.use_cases.send_admin_message import SendAdminMessageUseCase
from app.app_layer.use_cases.sync_user_profile import SyncUserProfileUseCase
from app.app_layer.use_cases.update_user_credentials import UpdateUserCredentialsUseCase
from app.app_layer.use_cases.update_user_settings import UpdateUserSettingsUseCase


class UseCasesContainer(containers.DeclarativeContainer):
    db = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()
    ssau = providers.DependenciesContainer()
    telegram = providers.DependenciesContainer()

    list_accounts_use_case: providers.Provider[IListAccountsUseCase] = providers.Factory(
        ListAccountsUseCase,
        uow_factory=db.uow_factory,
        account_repo=repositories.account_repo,
    )
    send_admin_message_use_case: providers.Provider[ISendAdminMessageUseCase] = providers.Factory(
        SendAdminMessageUseCase,
        notifier=telegram.notifier,
    )
    check_telegram_chats_use_case: providers.Provider[ICheckTelegramChatsUseCase] = (
        providers.Factory(
            CheckTelegramChatsUseCase,
            uow_factory=db.uow_factory,
            account_repo=repositories.account_repo,
            chat_checker=telegram.chat_checker,
        )
    )

    register_user_use_case: providers.Provider[IRegisterUserUseCase] = providers.Factory(
        RegisterUserUseCase,
        uow_factory=db.uow_factory,
        account_repo=repositories.account_repo,
    )
    update_user_credentials_use_case: providers.Provider[IUpdateUserCredentialsUseCase] = (
        providers.Factory(
            UpdateUserCredentialsUseCase,
            uow_factory=db.uow_factory,
            account_repo=repositories.account_repo,
        )
    )
    update_user_settings_use_case: providers.Provider[IUpdateUserSettingsUseCase] = (
        providers.Factory(
            UpdateUserSettingsUseCase,
            uow_factory=db.uow_factory,
            account_repo=repositories.account_repo,
        )
    )
    sync_user_profile_use_case: providers.Provider[ISyncUserProfileUseCase] = providers.Factory(
        SyncUserProfileUseCase,
        uow_factory=db.uow_factory,
        account_repo=repositories.account_repo,
        profile_provider=ssau.api_client,
    )
