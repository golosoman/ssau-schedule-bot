from pydantic import BaseModel, ConfigDict, field_validator


class Subgroup(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: int

    @field_validator("value")
    @classmethod
    def _validate(cls, value: int) -> int:
        if value < 1 or value > 2:
            raise ValueError("Subgroup must be 1 or 2.")
        return value

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)
