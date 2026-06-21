from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.repos.account.dto import AccountView


class NotificationServiceInputDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    account: AccountView
