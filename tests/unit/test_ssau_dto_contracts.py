from datetime import time

from app.app_layer.interfaces.http.ssau.dto.profile import GroupDto, UnifiedYearDto
from app.app_layer.interfaces.http.ssau.dto.schedule import ScheduleResponseDto
from app.infra.clients.ssau.ssau_schedule_mapper import map_schedule


def test_profile_dtos_parse() -> None:
    group_payload = {"id": 755932538, "name": "6132-020402D"}
    group = GroupDto.model_validate(group_payload)
    assert group.id == 755932538
    assert group.name == "6132-020402D"

    year_payload = {
        "id": 14,
        "year": 2025,
        "startDate": "2025-09-01",
        "endDate": "2026-08-30",
        "weeks": 52,
        "isCurrent": True,
        "isElongated": False,
    }
    year = UnifiedYearDto.model_validate(year_payload)
    assert year.id == 14
    assert year.year == 2025
    assert year.start_date.isoformat() == "2025-09-01"
    assert year.is_current is True


def test_schedule_mapping() -> None:
    payload = {
        "lessons": [
            {
                "id": 1,
                "discipline": {"name": "Math"},
                "teachers": [{"name": "Ivanov"}],
                "weekday": {"id": 1},
                "weeks": [{"week": 1, "isOnline": True}],
                "time": {"beginTime": "08:30", "endTime": "10:00"},
                "conference": {"url": "https://bbb.example/room"},
                "groups": [{"subgroup": 1}],
                "weeklyDetail": False,
            }
        ]
    }
    dto = ScheduleResponseDto.model_validate(payload)
    lessons = map_schedule(dto)
    assert len(lessons) == 1
    lesson = lessons[0]
    assert lesson.subject == "Math"
    assert lesson.teacher == "Ivanov"
    assert lesson.is_online is True
    assert lesson.conference_url == "https://bbb.example/room"
    assert lesson.time.start == time(8, 30)
    assert lesson.time.end == time(10, 0)
