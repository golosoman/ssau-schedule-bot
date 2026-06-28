from datetime import date

from pydantic import BaseModel, ConfigDict


class WeekCalculatorServiceInputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    start_date: date
    target_date: date


class WeekCalculatorServiceOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    week_number: int
