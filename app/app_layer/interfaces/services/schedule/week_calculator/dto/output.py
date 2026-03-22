from pydantic import BaseModel, ConfigDict


class WeekCalculatorServiceOutputDTO(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    week_number: int
