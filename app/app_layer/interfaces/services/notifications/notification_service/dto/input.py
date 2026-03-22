from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.domain.entities.users import User


class NotificationServiceInputDTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    uow: IUnitOfWork
    user: User
