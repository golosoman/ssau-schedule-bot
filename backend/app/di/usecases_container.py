from dependency_injector import containers, providers

from app.app_layer.interfaces.use_cases.authenticate_user.interface import (
    IAuthenticateUserUseCase,
)
from app.app_layer.interfaces.use_cases.check_telegram_chats.interface import (
    ICheckTelegramChatsUseCase,
)
from app.app_layer.interfaces.use_cases.get_schedule_for_date.interface import (
    IGetScheduleForDateUseCase,
)
from app.app_layer.interfaces.use_cases.get_upcoming_lesson.interface import (
    IGetUpcomingLessonUseCase,
)
from app.app_layer.interfaces.use_cases.list_accounts.interface import IListAccountsUseCase
from app.app_layer.interfaces.use_cases.refresh_schedule.interface import (
    IRefreshScheduleUseCase,
)
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
from app.app_layer.use_cases.authenticate_user import AuthenticateUserUseCase
from app.app_layer.use_cases.check_telegram_chats import CheckTelegramChatsUseCase
from app.app_layer.use_cases.get_schedule_for_date import GetScheduleForDateUseCase
from app.app_layer.use_cases.get_upcoming_lesson import GetUpcomingLessonUseCase
from app.app_layer.use_cases.list_accounts import ListAccountsUseCase
from app.app_layer.use_cases.refresh_schedule import RefreshScheduleUseCase
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
    services = providers.DependenciesContainer()

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
    get_upcoming_lesson_use_case: providers.Provider[IGetUpcomingLessonUseCase] = providers.Factory(
        GetUpcomingLessonUseCase,
        schedule_sync_service=services.schedule_sync_service,
        week_calculator=services.week_calculator_service,
        upcoming_lesson_service=services.upcoming_lesson_service,
    )
    get_schedule_for_date_use_case: providers.Provider[IGetScheduleForDateUseCase] = (
        providers.Factory(
            GetScheduleForDateUseCase,
            schedule_sync_service=services.schedule_sync_service,
            week_calculator=services.week_calculator_service,
            daily_schedule_service=services.daily_schedule_service,
        )
    )
    refresh_schedule_use_case: providers.Provider[IRefreshScheduleUseCase] = providers.Factory(
        RefreshScheduleUseCase,
        schedule_sync_service=services.schedule_sync_service,
    )
    authenticate_user_use_case: providers.Provider[IAuthenticateUserUseCase] = providers.Factory(
        AuthenticateUserUseCase,
        update_credentials_use_case=update_user_credentials_use_case,
        sync_profile_use_case=sync_user_profile_use_case,
    )
