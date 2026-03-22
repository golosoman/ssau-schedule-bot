from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.subgroup import Subgroup


class UpdateUserSettingsUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    chat_id: int
    subgroup: Subgroup | None = None
    user_type: str | None = None
    notify_enabled: bool | None = None
