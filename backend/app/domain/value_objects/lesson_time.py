from datetime import time

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class LessonTime(BaseModel):
    model_config = ConfigDict(frozen=True)

    start: time
    end: time

    @field_validator("start", "end")
    @classmethod
    def _validate_time(cls, value: time) -> time:
        if value.tzinfo is not None:
            raise ValueError("LessonTime must not include timezone.")
        return value

    @model_validator(mode="after")
    def _validate_range(self) -> "LessonTime":
        if self.end <= self.start:
            raise ValueError("LessonTime end must be after start.")
        return self

    def format_range(self) -> str:
        return f"{self.start.strftime('%H:%M')}-{self.end.strftime('%H:%M')}"
