from __future__ import annotations

from collections.abc import Iterable

from aiogram.types import MessageEntity
from aiogram.utils.formatting import Bold, Code, Italic, Text

try:
    from aiogram.utils.formatting import TextLink as _TextLink

    def _make_link(text: str, url: str) -> object:
        return _TextLink(text, url=url)
except ImportError:  # pragma: no cover - compatibility shim
    from aiogram.utils.formatting import Link as _TextLink

    def _make_link(text: str, url: str) -> object:
        return _TextLink(text, url)

from app.app_layer.interfaces.telegram.renderer.dto import (
    RenderedTelegramMessage,
    TelegramEntity,
)
from app.app_layer.interfaces.telegram.renderer.interface import TelegramMessageRenderer
from app.domain.entities.lesson import Lesson
from app.domain.messages import ErrorMessage, InfoMessage, NotificationMessage, ScheduleMessage
from app.domain.messages.base import TelegramMessage


class AiogramTelegramMessageRenderer(TelegramMessageRenderer):
    def render(self, message: TelegramMessage) -> RenderedTelegramMessage:
        if isinstance(message, ScheduleMessage):
            return self._render_schedule(message)
        if isinstance(message, NotificationMessage):
            return self._render_notification(message)
        if isinstance(message, InfoMessage):
            return self._render_info(message)
        if isinstance(message, ErrorMessage):
            return self._render_error(message)
        raise TypeError(f"Unsupported message type: {type(message)!r}")

    def _render_schedule(self, message: ScheduleMessage) -> RenderedTelegramMessage:
        parts: list[object] = [
            Bold(message.title),
            "\n",
            "Дата: ",
            Code(message.date.isoformat()),
        ]

        if not message.lessons:
            parts.extend(["\n\n", "Занятий нет."])
            return self._as_rendered(Text(*parts))

        lessons = sorted(message.lessons, key=lambda lesson: lesson.time.start)
        for lesson in lessons:
            parts.extend(["\n\n", self._lesson_card(lesson, include_time=True)])
        return self._as_rendered(Text(*parts))

    def _render_notification(self, message: NotificationMessage) -> RenderedTelegramMessage:
        start_label = message.lesson_start.strftime("%Y-%m-%d %H:%M")
        parts: list[object] = [
            Bold(message.title),
            "\n",
            "Начало: ",
            Code(start_label),
            "\n\n",
            self._lesson_card(message.lesson, include_time=True),
        ]
        return self._as_rendered(Text(*parts))

    def _render_info(self, message: InfoMessage) -> RenderedTelegramMessage:
        parts: list[object] = [Bold(message.title)]
        if message.lines:
            parts.append("\n")
            parts.extend(self._bulleted_lines(message.lines))
        return self._as_rendered(Text(*parts))

    def _render_error(self, message: ErrorMessage) -> RenderedTelegramMessage:
        parts: list[object] = [Bold(message.title)]
        if message.details:
            parts.append("\n")
            parts.extend(self._bulleted_lines(message.details))
        return self._as_rendered(Text(*parts))

    @staticmethod
    def _lesson_card(lesson: Lesson, *, include_time: bool) -> Text:
        teacher = lesson.teacher or "Преподаватель не указан"
        mode_label = "онлайн" if lesson.is_online else "очно"
        subject = Text(Bold(lesson.subject), " (", Italic(lesson.type), ")")

        parts: list[object] = [subject]
        if include_time:
            parts.extend(["\n", "- Время: ", Code(lesson.time.format_range())])
        parts.extend(
            [
                "\n",
                "- Преподаватель: ",
                teacher,
                "\n",
                "- Формат: ",
                mode_label,
            ]
        )
        if lesson.conference_url:
            parts.extend(
                [
                    "\n",
                    "- Ссылка: ",
                    _make_link("Открыть конференцию", lesson.conference_url),
                ]
            )
        return Text(*parts)

    @staticmethod
    def _bulleted_lines(lines: Iterable[str]) -> list[object]:
        parts: list[object] = []
        for idx, line in enumerate(lines):
            if idx:
                parts.append("\n")
            parts.extend(["- ", line])
        return parts

    @staticmethod
    def _as_rendered(text: Text) -> RenderedTelegramMessage:
        payload = text.as_kwargs()
        entities = tuple(_to_entity(entity) for entity in payload.get("entities", []))
        return RenderedTelegramMessage(text=payload["text"], entities=entities)


def _to_entity(entity: MessageEntity) -> TelegramEntity:
    return TelegramEntity(
        type=str(entity.type),
        offset=entity.offset,
        length=entity.length,
        url=entity.url,
        language=entity.language,
    )
