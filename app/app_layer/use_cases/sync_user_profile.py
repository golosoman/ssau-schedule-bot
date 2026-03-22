import logging
from collections.abc import Callable

from app.app_layer.interfaces.http.ssau.interface import ISSAUProfileProvider
from app.app_layer.interfaces.use_cases.sync_user_profile.dto.input import (
    SyncUserProfileUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.dto.output import (
    SyncUserProfileUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.sync_user_profile.interface import (
    ISyncUserProfileUseCase,
)
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.domain.constants import DEFAULT_SUBGROUP_VALUE, DEFAULT_USER_TYPE
from app.domain.value_objects.subgroup import Subgroup

logger = logging.getLogger(__name__)


class SyncUserProfileUseCase(ISyncUserProfileUseCase):
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        profile_provider: ISSAUProfileProvider,
    ) -> None:
        self._uow_factory = uow_factory
        self._profile_provider = profile_provider

    async def execute(
        self,
        input_dto: SyncUserProfileUseCaseInputDTO,
    ) -> SyncUserProfileUseCaseOutputDTO:
        user = input_dto.user
        if user.ssau.credentials is None:
            raise RuntimeError("User credentials are required to sync profile.")

        profile = await self._profile_provider.fetch_profile(
            user.ssau.credentials.login,
            user.ssau.credentials.password,
        )
        existing = user.ssau.profile
        subgroup = (
            existing.profile_details.subgroup
            if existing is not None
            else Subgroup(value=DEFAULT_SUBGROUP_VALUE)
        )
        user_type = (
            existing.profile_details.user_type if existing is not None else DEFAULT_USER_TYPE
        )
        details = profile.profile_details.model_copy(
            update={
                "subgroup": subgroup,
                "user_type": user_type,
            }
        )
        user.ssau.profile = profile.model_copy(
            update={
                "profile_details": details,
            }
        )

        logger.info(
            "SSAU group updated: %s (%s)",
            profile.profile_details.group_name,
            profile.profile_ids.group_id,
        )
        logger.info("SSAU year updated: %s", profile.profile_ids.year_id)

        async with self._uow_factory() as uow:
            return SyncUserProfileUseCaseOutputDTO(user=await uow.users.upsert(user))
