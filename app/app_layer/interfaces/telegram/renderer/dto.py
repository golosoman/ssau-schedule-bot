from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramEntity:
    type: str
    offset: int
    length: int
    url: str | None = None
    language: str | None = None


@dataclass(frozen=True)
class RenderedTelegramMessage:
    text: str
    entities: tuple[TelegramEntity, ...] = ()

    @property
    def length(self) -> int:
        return len(self.text)
