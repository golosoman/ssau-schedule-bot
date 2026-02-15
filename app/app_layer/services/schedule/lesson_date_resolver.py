from datetime import date, datetime

from app.domain.entities.lesson import Lesson


class LessonDateResolver:

    @staticmethod
    def resolve_datetime(
        lesson: Lesson,
        target_date: date,
    ) -> tuple[datetime, datetime]:

        start_dt = datetime.combine(target_date, lesson.time.start)
        end_dt = datetime.combine(target_date, lesson.time.end)

        return start_dt, end_dt
