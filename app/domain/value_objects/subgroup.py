from pydantic import BaseModel, ConfigDict, field_validator

from app.domain.constants import SubgroupValue


class Subgroup(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: SubgroupValue

    @field_validator("value", mode="before")
    @classmethod
    def _parse(cls, value: object) -> SubgroupValue:
        if isinstance(value, SubgroupValue):
            return value
        if isinstance(value, str):
            raw = value.strip().lower()
            if raw == "all":
                return SubgroupValue.ALL
            if raw.isdigit():
                value = int(raw)
        try:
            return SubgroupValue(value)  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            raise ValueError("Subgroup must be 1, 2, or all.") from exc

    @property
    def is_all(self) -> bool:
        return self.value == SubgroupValue.ALL

    @classmethod
    def all(cls) -> "Subgroup":
        return cls(value=SubgroupValue.ALL)

    def __int__(self) -> int:
        return int(self.value)

    def __str__(self) -> str:
        if self.is_all:
            return "all"
        return str(int(self.value))
