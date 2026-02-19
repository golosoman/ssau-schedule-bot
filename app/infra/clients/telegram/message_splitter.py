from __future__ import annotations

from app.app_layer.interfaces.telegram.renderer.dto import (
    RenderedTelegramMessage,
    TelegramEntity,
)
from app.domain.constants import TELEGRAM_MESSAGE_MAX_LENGTH


def split_message(
    message: RenderedTelegramMessage,
    *,
    limit: int = TELEGRAM_MESSAGE_MAX_LENGTH,
) -> list[RenderedTelegramMessage]:
    if message.length <= limit:
        return [message]

    chunks: list[RenderedTelegramMessage] = []
    start = 0
    text = message.text
    entities = message.entities

    while start < len(text):
        max_end = min(start + limit, len(text))
        if max_end == len(text):
            chunks.append(
                RenderedTelegramMessage(
                    text=text[start:max_end],
                    entities=_slice_entities(entities, start, max_end),
                )
            )
            break

        split_at = _find_split_point(text, entities, start, max_end)
        if split_at <= start:
            split_at = max_end

        chunks.append(
            RenderedTelegramMessage(
                text=text[start:split_at],
                entities=_slice_entities(entities, start, split_at),
            )
        )
        start = split_at

    return chunks


def _find_split_point(
    text: str,
    entities: tuple[TelegramEntity, ...],
    start: int,
    max_end: int,
) -> int:
    for separator in ("\n\n", "\n", " "):
        idx = text.rfind(separator, start, max_end)
        while idx != -1:
            candidate = idx + len(separator)
            if candidate > start and _is_boundary_safe(candidate, entities):
                return candidate
            idx = text.rfind(separator, start, idx)
    return max_end


def _is_boundary_safe(position: int, entities: tuple[TelegramEntity, ...]) -> bool:
    for entity in entities:
        start = entity.offset
        end = entity.offset + entity.length
        if start < position < end:
            return False
    return True


def _slice_entities(
    entities: tuple[TelegramEntity, ...],
    chunk_start: int,
    chunk_end: int,
) -> tuple[TelegramEntity, ...]:
    sliced: list[TelegramEntity] = []
    for entity in entities:
        entity_start = entity.offset
        entity_end = entity.offset + entity.length
        if entity_end <= chunk_start or entity_start >= chunk_end:
            continue
        slice_start = max(entity_start, chunk_start)
        slice_end = min(entity_end, chunk_end)
        sliced.append(
            TelegramEntity(
                type=entity.type,
                offset=slice_start - chunk_start,
                length=slice_end - slice_start,
                url=entity.url,
                language=entity.language,
            )
        )
    return tuple(sliced)
