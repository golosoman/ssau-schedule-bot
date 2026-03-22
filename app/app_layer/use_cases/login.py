from app.app_layer.interfaces.http.ssau.interface import IAuthRepository
from app.app_layer.interfaces.use_cases.login.dto.input import LoginUseCaseInputDTO
from app.app_layer.interfaces.use_cases.login.dto.output import LoginUseCaseOutputDTO
from app.app_layer.interfaces.use_cases.login.interface import ILoginUseCase


class LoginUseCase(ILoginUseCase):
    def __init__(self, repository: IAuthRepository) -> None:
        self._repository = repository

    async def execute(self, input_dto: LoginUseCaseInputDTO) -> LoginUseCaseOutputDTO:
        return LoginUseCaseOutputDTO(
            session=await self._repository.login(input_dto.login, input_dto.password)
        )
