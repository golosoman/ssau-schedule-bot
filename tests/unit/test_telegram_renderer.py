from __future__ import annotations

from datetime import date, time

from app.app_layer.interfaces.telegram.renderer.dto import RenderedTelegramMessage, TelegramEntity
from app.domain.entities.lesson import Lesson
from app.domain.messages.info import InfoMessage
from app.domain.messages.schedule import ScheduleMessage
from app.domain.value_objects.lesson_time import LessonTime
from app.infra.clients.telegram.message_renderer import AiogramTelegramMessageRenderer
from app.infra.clients.telegram.message_splitter import split_message


def test_renderer_schedule_formatting() -> None:
    lesson = Lesson(
        id=1,
        type="Лекция",
        subject="Алгоритмы",
        teacher="Иванов И.И.",
        weekday=1,
        week_numbers=[1],
        time=LessonTime(start=time(9, 0), end=time(10, 30)),
        is_online=True,
        conference_url="https://example.com",
        subgroup=None,
    )
    message = ScheduleMessage(
        title="Расписание на сегодня",
        date=date(2025, 9, 1),
        lessons=[lesson],
    )

    rendered = AiogramTelegramMessageRenderer().render(message)

    assert "Расписание" in rendered.text
    assert "Алгоритмы" in rendered.text
    assert "Лекция" in rendered.text
    assert lesson.time.format_range() in rendered.text
    assert any(entity.type == "bold" for entity in rendered.entities)


def test_split_message_respects_limit() -> None:
    text = "line\n" * 30
    message = RenderedTelegramMessage(text=text)

    chunks = split_message(message, limit=50)

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 50 for chunk in chunks)
    assert "".join(chunk.text for chunk in chunks) == text


def test_split_message_slices_entities() -> None:
    text = "0123456789ABCDEFGHIJ"
    entity = TelegramEntity(type="bold", offset=5, length=10)
    message = RenderedTelegramMessage(text=text, entities=(entity,))

    chunks = split_message(message, limit=10)

    assert len(chunks) == 2
    assert chunks[0].entities[0].offset == 5
    assert chunks[0].entities[0].length == 5
    assert chunks[1].entities[0].offset == 0
    assert chunks[1].entities[0].length == 5


def test_renderer_preserves_special_chars() -> None:
    message = InfoMessage(
        title="Символы",
        lines=["<tag> & _ * [ ] ( )"],
    )

    rendered = AiogramTelegramMessageRenderer().render(message)

    assert "<tag> & _ * [ ] ( )" in rendered.text
