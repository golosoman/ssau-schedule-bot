from app.app_layer.interfaces.services.schedule.week_calculator.dto.input import (
    WeekCalculatorServiceInputDTO,
)
from app.app_layer.interfaces.services.schedule.week_calculator.interface import (
    IWeekCalculatorService,
)
from app.app_layer.interfaces.http.ssau.interface import IScheduleRepository
from app.app_layer.interfaces.use_cases.get_schedule.dto.input import GetScheduleUseCaseInputDTO
from app.app_layer.interfaces.use_cases.get_schedule.dto.output import GetScheduleUseCaseOutputDTO
from app.app_layer.interfaces.use_cases.get_schedule.interface import IGetScheduleUseCase


class GetScheduleUseCase(IGetScheduleUseCase):
    def __init__(
        self,
        repository: IScheduleRepository,
        week_calculator: IWeekCalculatorService,
    ) -> None:
        self._repository = repository
        self._week_calculator = week_calculator

    async def execute(self, input_dto: GetScheduleUseCaseInputDTO) -> GetScheduleUseCaseOutputDTO:
        target_date = input_dto.target_date
        week_output = self._week_calculator.get_week_number(
            WeekCalculatorServiceInputDTO(
                start_date=input_dto.academic_year_start,
                target_date=target_date,
            )
        )
        week_number = week_output.week_number

        weekday = target_date.isoweekday()

        lessons = await self._repository.get_schedule(week_number)

        return GetScheduleUseCaseOutputDTO(
            lessons=[
                lesson
                for lesson in lessons
                if week_number in lesson.week_numbers and lesson.weekday == weekday
            ]
        )
