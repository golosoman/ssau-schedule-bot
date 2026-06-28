from app.app_layer.interfaces.use_cases.authenticate_user.dto import (
    AuthenticateUserUseCaseInputDTO,
    AuthenticateUserUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.authenticate_user.enums import (
    AuthenticateUserStatusEnum,
)
from app.app_layer.interfaces.use_cases.authenticate_user.interface import (
    IAuthenticateUserUseCase,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.dto import (
    SyncUserProfileUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.dto import (
    UpdateUserCredentialsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.update_user_credentials.interface import (
    IUpdateUserCredentialsUseCase,
)
from app.logging.config import get_logger

logger = get_logger(__name__)


class AuthenticateUserUseCase(IAuthenticateUserUseCase):
    """Аутентификация: сохранить логин/пароль СНИУ и подтянуть профиль (группа/год).

    Креды сохраняются всегда; профиль может не подтянуться — об этом сообщает статус.
    """

    def __init__(
        self,
        update_credentials_use_case: IUpdateUserCredentialsUseCase,
        sync_profile_use_case: ISyncUserProfileUseCase,
    ) -> None:
        self._update_credentials_use_case = update_credentials_use_case
        self._sync_profile_use_case = sync_profile_use_case

    async def execute(
        self,
        input_dto: AuthenticateUserUseCaseInputDTO,
    ) -> AuthenticateUserUseCaseOutputDTO:
        account = (
            await self._update_credentials_use_case.execute(
                UpdateUserCredentialsUseCaseInputDTO(
                    chat_id=input_dto.chat_id,
                    login=input_dto.login,
                    password=input_dto.password,
                )
            )
        ).account

        try:
            account = (
                await self._sync_profile_use_case.execute(
                    SyncUserProfileUseCaseInputDTO(account=account)
                )
            ).account
        except Exception:
            logger.exception(
                "Profile sync failed during authentication for chat %s.", input_dto.chat_id
            )
            return AuthenticateUserUseCaseOutputDTO(
                status=AuthenticateUserStatusEnum.PROFILE_FETCH_ERROR, account=account
            )

        if account.ssau_profile is None:
            return AuthenticateUserUseCaseOutputDTO(
                status=AuthenticateUserStatusEnum.PROFILE_NOT_FOUND, account=account
            )
        return AuthenticateUserUseCaseOutputDTO(
            status=AuthenticateUserStatusEnum.SUCCESS, account=account
        )
