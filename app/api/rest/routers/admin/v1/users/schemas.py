from datetime import datetime

from pydantic import BaseModel

from app.app_layer.interfaces.repos.account.dto import AccountView
from app.app_layer.interfaces.use_cases.list_accounts.dto.output import (
    ListAccountsUseCaseOutputDTO,
)


class V1AccountOutputSchema(BaseModel):
    id: int
    chat_id: int
    display_name: str
    created_at: datetime
    notifications_enabled: bool
    is_authed: bool
    is_provisioned: bool
    group_name: str | None
    user_type: str | None
    subgroup: str | None

    @classmethod
    def from_view(cls, view: AccountView) -> "V1AccountOutputSchema":
        profile = view.ssau_profile
        return cls(
            id=view.account_id,
            chat_id=view.chat_id,
            display_name=view.telegram.display_name,
            created_at=view.account.created_at,
            notifications_enabled=view.settings.schedule_notifications_enabled,
            is_authed=view.is_authed,
            is_provisioned=view.is_provisioned,
            group_name=profile.group_name if profile else None,
            user_type=profile.user_type if profile else None,
            subgroup=str(profile.subgroup) if profile else None,
        )


class V1ListAccountsOutputSchema(BaseModel):
    accounts: list[V1AccountOutputSchema]

    @classmethod
    def from_use_case_dto(cls, dto: ListAccountsUseCaseOutputDTO) -> "V1ListAccountsOutputSchema":
        return cls(accounts=[V1AccountOutputSchema.from_view(a) for a in dto.accounts])
