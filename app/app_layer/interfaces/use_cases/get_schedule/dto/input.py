from datetime import date

from pydantic import BaseModel, ConfigDict


class GetScheduleUseCaseInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    academic_year_start: date
    target_date: date
