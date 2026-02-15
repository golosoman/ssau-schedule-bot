from app.app_layer.interfaces.http.ssau.dto.schedule import ScheduleResponseDto
from app.domain.entities.lesson import Lesson
from app.domain.value_objects.lesson_time import LessonTime


def map_schedule(data: ScheduleResponseDto) -> list[Lesson]:
    lessons: list[Lesson] = []

    for item in data.lessons:
        teacher_name = item.teachers[0].name if item.teachers else ""
        subject = item.discipline.name
        weekday = item.weekday.id
        week_numbers = [w.week for w in item.weeks]
        is_online = any(w.is_online for w in item.weeks)
        conference_url = item.conference.url if item.conference else None
        subgroup = item.groups[0].subgroup if item.groups else None

        lessons.append(
            Lesson(
                id=item.id,
                subject=subject,
                teacher=teacher_name,
                weekday=weekday,
                week_numbers=week_numbers,
                time=LessonTime(
                    start=item.time.begin_time,
                    end=item.time.end_time,
                ),
                is_online=is_online,
                conference_url=conference_url,
                subgroup=subgroup,
                weekly_detail=item.weekly_detail,
            )
        )

    return lessons
