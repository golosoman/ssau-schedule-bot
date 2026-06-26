from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountViewDTO


class NotificationServiceInputDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    account: AccountViewDTO


class NotificationServiceOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    sent_count: int
