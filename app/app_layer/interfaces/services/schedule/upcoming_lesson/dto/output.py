from pydantic import BaseModel, ConfigDict

from app.app_layer.interfaces.schedule.upcoming_lesson.dto import UpcomingLesson


class UpcomingLessonServiceOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    upcoming_lesson: UpcomingLesson | None
