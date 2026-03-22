from pydantic import BaseModel, ConfigDict

from app.domain.entities.users import User


class SyncUserProfileUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    user: User
