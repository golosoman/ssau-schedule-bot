from __future__ import annotations

from typing import Protocol


class Notifier(Protocol):
    async def send(self, chat_id: int, text: str) -> None:
        ...
