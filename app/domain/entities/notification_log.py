from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class NotificationLog(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    user_id: int
    lesson_id: int
    lesson_date: date
    sent_at: datetime
