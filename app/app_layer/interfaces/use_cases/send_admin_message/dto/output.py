from pydantic import BaseModel, ConfigDict


class SendAdminMessageUseCaseOutputDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    sent: list[int]
    failed: list[int]
