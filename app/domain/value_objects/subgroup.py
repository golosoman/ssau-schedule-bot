from pydantic import BaseModel, ConfigDict, field_validator

from app.domain.constants import SubgroupValueEnum


class Subgroup(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: SubgroupValueEnum

    @field_validator("value", mode="before")
    @classmethod
    def _parse(cls, value: object) -> SubgroupValueEnum:
        if isinstance(value, SubgroupValueEnum):
            return value
        if isinstance(value, str):
            raw = value.strip().lower()
            if raw == "all":
                return SubgroupValueEnum.ALL
            if raw.isdigit():
                value = int(raw)
        try:
            return SubgroupValueEnum(value)  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            raise ValueError("Subgroup must be 1, 2, or all.") from exc

    @property
    def is_all(self) -> bool:
        return self.value == SubgroupValueEnum.ALL

    @classmethod
    def all(cls) -> "Subgroup":
        return cls(value=SubgroupValueEnum.ALL)

    @classmethod
    def parse(cls, value: object) -> "Subgroup":
        """Build from a raw value (str/int/SubgroupValueEnum); validator coerces it."""
        return cls(value=value)  # type: ignore[arg-type]

    def __int__(self) -> int:
        return int(self.value)

    def __str__(self) -> str:
        if self.is_all:
            return "all"
        return str(int(self.value))
