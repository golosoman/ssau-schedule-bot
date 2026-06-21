from pydantic import BaseModel

from app.app_layer.interfaces.use_cases.send_admin_message.dto.output import (
    SendAdminMessageUseCaseOutputDTO,
)


class V1SendMessageInputSchema(BaseModel):
    chat_ids: list[int]
    text: str


class V1SendMessageOutputSchema(BaseModel):
    sent: list[int]
    failed: list[int]

    @classmethod
    def from_use_case_dto(
        cls, dto: SendAdminMessageUseCaseOutputDTO
    ) -> "V1SendMessageOutputSchema":
        return cls(sent=dto.sent, failed=dto.failed)
