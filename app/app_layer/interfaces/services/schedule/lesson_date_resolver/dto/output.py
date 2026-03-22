from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LessonDateResolverServiceOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    start_datetime: datetime
    end_datetime: datetime
