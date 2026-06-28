from collections.abc import Callable

from app.app_layer.interfaces.http.ssau.api.interface import ISsauApiClient
from app.app_layer.interfaces.repos.account.dto import (
    SsauProfileCreateDTO,
    SsauProfileUpdateDTO,
)
from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.app_layer.interfaces.use_cases.sync_user_profile.dto import (
    SyncUserProfileUseCaseInputDTO,
    SyncUserProfileUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.domain.constants import DEFAULT_SUBGROUP_VALUE
from app.domain.value_objects.subgroup import Subgroup
from app.logging.config import get_logger

logger = get_logger(__name__)


class SyncUserProfileUseCase(ISyncUserProfileUseCase):
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        account_repo: IAccountRepository,
        profile_provider: ISsauApiClient,
    ) -> None:
        self._uow_factory = uow_factory
        self._account_repo = account_repo
        self._profile_provider = profile_provider

    async def execute(
        self,
        input_dto: SyncUserProfileUseCaseInputDTO,
    ) -> SyncUserProfileUseCaseOutputDTO:
        account = input_dto.account
        if account.ssau_identity is None:
            raise RuntimeError("User credentials are required to sync profile.")

        fetched = await self._profile_provider.fetch_profile(
            account.ssau_identity.login,
            account.ssau_identity.password,
        )
        logger.info(
            "SSAU profile fetched: group=%s year=%s",
            fetched.group_id.value,
            fetched.year_id.value,
        )

        async with self._uow_factory():
            existing = account.ssau_profile
            if existing is not None:
                await self._account_repo.update_ssau_profile(
                    SsauProfileUpdateDTO(
                        id=existing.id,
                        group_id=fetched.group_id,
                        year_id=fetched.year_id,
                        group_name=fetched.group_name,
                        academic_year_start=fetched.academic_year_start,
                        subgroup=existing.subgroup,
                        user_type=existing.user_type,
                    )
                )
            else:
                await self._account_repo.create_ssau_profile(
                    SsauProfileCreateDTO(
                        ssau_identity_id=account.ssau_identity.id,
                        group_id=fetched.group_id,
                        year_id=fetched.year_id,
                        group_name=fetched.group_name,
                        academic_year_start=fetched.academic_year_start,
                        subgroup=Subgroup(value=DEFAULT_SUBGROUP_VALUE),
                        user_type=fetched.user_type,
                    )
                )

            view = await self._account_repo.get_by_chat_id(account.chat_id)
            if view is None:
                raise RuntimeError("Account not found after write.")
            return SyncUserProfileUseCaseOutputDTO(account=view)
