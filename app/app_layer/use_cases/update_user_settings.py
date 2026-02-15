from typing import Callable

from app.app_layer.interfaces.uow.unit_of_work.interface import UnitOfWork
from app.domain.entities.user import User
from app.domain.value_objects.subgroup import Subgroup


class UpdateUserSettingsUseCase:

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def execute(
        self,
        chat_id: int,
        *,
        subgroup: Subgroup | None = None,
        user_type: str | None = None,
        notify_enabled: bool | None = None,
    ) -> User:
        async with self._uow_factory() as uow:
            user = await uow.users.get_by_chat_id(chat_id)
            if user is None:
                raise RuntimeError("User is not registered.")

            if subgroup is not None or user_type is not None:
                if user.ssau.profile is None:
                    raise RuntimeError("User SSAU profile is required to update settings.")
                updates = {}
                if subgroup is not None:
                    updates["subgroup"] = subgroup
                if user_type is not None:
                    updates["user_type"] = user_type
                user.ssau.profile = user.ssau.profile.model_copy(update=updates)
            if notify_enabled is not None:
                user.telegram.notify_enabled = notify_enabled

            return await uow.users.upsert(user)
