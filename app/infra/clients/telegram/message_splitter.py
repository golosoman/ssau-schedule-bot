from app.app_layer.interfaces.telegram.renderer.dto import (
    RenderedTelegramMessageDTO,
    TelegramEntityDTO,
)
from app.domain.constants import TELEGRAM_MESSAGE_MAX_LENGTH


def split_message(
    message: RenderedTelegramMessageDTO,
    *,
    limit: int = TELEGRAM_MESSAGE_MAX_LENGTH,
) -> list[RenderedTelegramMessageDTO]:
    if message.length <= limit:
        return [message]

    chunks: list[RenderedTelegramMessageDTO] = []
    start = 0
    text = message.text
    entities = message.entities

    while start < len(text):
        max_end = min(start + limit, len(text))
        if max_end == len(text):
            chunks.append(
                RenderedTelegramMessageDTO(
                    text=text[start:max_end],
                    entities=_slice_entities(entities, start, max_end),
                )
            )
            break

        split_at = _find_split_point(text, entities, start, max_end)
        if split_at <= start:
            split_at = max_end

        chunks.append(
            RenderedTelegramMessageDTO(
                text=text[start:split_at],
                entities=_slice_entities(entities, start, split_at),
            )
        )
        start = split_at

    return chunks


def _find_split_point(
    text: str,
    entities: tuple[TelegramEntityDTO, ...],
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


def _is_boundary_safe(position: int, entities: tuple[TelegramEntityDTO, ...]) -> bool:
    for entity in entities:
        start = entity.offset
        end = entity.offset + entity.length
        if start < position < end:
            return False
    return True


def _slice_entities(
    entities: tuple[TelegramEntityDTO, ...],
    chunk_start: int,
    chunk_end: int,
) -> tuple[TelegramEntityDTO, ...]:
    sliced: list[TelegramEntityDTO] = []
    for entity in entities:
        entity_start = entity.offset
        entity_end = entity.offset + entity.length
        if entity_end <= chunk_start or entity_start >= chunk_end:
            continue
        slice_start = max(entity_start, chunk_start)
        slice_end = min(entity_end, chunk_end)
        sliced.append(
            TelegramEntityDTO(
                type=entity.type,
                offset=slice_start - chunk_start,
                length=slice_end - slice_start,
                url=entity.url,
                language=entity.language,
            )
        )
    return tuple(sliced)
