from app.app_layer.interfaces.http.ssau.interface import AuthRepository
from app.domain.entities.auth import AuthSession


class LoginUseCase:

    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    async def execute(self, login: str, password: str) -> AuthSession:
        return await self._repository.login(login, password)
