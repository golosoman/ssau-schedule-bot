from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramEntityDTO:
    type: str
    offset: int
    length: int
    url: str | None = None
    language: str | None = None


@dataclass(frozen=True)
class RenderedTelegramMessageDTO:
    text: str
    entities: tuple[TelegramEntityDTO, ...] = ()

    @property
    def length(self) -> int:
        return len(self.text)
