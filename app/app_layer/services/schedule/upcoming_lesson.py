from __future__ import annotations

from datetime import datetime, timedelta

from app.app_layer.interfaces.schedule.upcoming_lesson.dto import UpcomingLesson
from app.domain.entities.lesson import Lesson
from app.domain.value_objects.subgroup import Subgroup


class UpcomingLessonService:
    @staticmethod
    def find_next(
        lessons: list[Lesson],
        now_local: datetime,
        week_number: int,
        subgroup: Subgroup,
    ) -> UpcomingLesson | None:
        candidates: list[UpcomingLesson] = []
        today = now_local.date()
        tz = now_local.tzinfo

        for offset in range(0, 7):
            target_date = today + timedelta(days=offset)
            weekday = target_date.isoweekday()
            for lesson in lessons:
                if lesson.weekday != weekday:
                    continue
                if week_number not in lesson.week_numbers:
                    continue
                if not _lesson_matches_subgroup(lesson.subgroup, subgroup):
                    continue
                start_at = datetime.combine(target_date, lesson.time.start, tzinfo=tz)
                if start_at < now_local:
                    continue
                candidates.append(UpcomingLesson(lesson=lesson, start_at=start_at))

        if not candidates:
            return None

        return min(candidates, key=lambda item: item.start_at)


def _lesson_matches_subgroup(lesson_subgroup: int | None, subgroup: Subgroup) -> bool:
    if lesson_subgroup is None:
        return True
    return lesson_subgroup == subgroup.value
