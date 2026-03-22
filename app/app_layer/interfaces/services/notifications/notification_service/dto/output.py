from pydantic import BaseModel, ConfigDict


class NotificationServiceOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    sent_count: int
