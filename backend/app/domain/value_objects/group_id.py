from pydantic import BaseModel, ConfigDict, field_validator


class GroupId(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: int

    @field_validator("value")
    @classmethod
    def _validate(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("GroupId must be positive.")
        return value

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)
