from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, field_validator


class Timezone(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: str

    @field_validator("value")
    @classmethod
    def _validate(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: {value}") from exc
        return value

    def tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.value)

    def __str__(self) -> str:
        return self.value
