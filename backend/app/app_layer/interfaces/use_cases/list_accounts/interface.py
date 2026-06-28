from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.list_accounts.dto import (
    ListAccountsUseCaseOutputDTO,
)


class IListAccountsUseCase(ABC):
    @abstractmethod
    async def execute(self) -> ListAccountsUseCaseOutputDTO:
        raise NotImplementedError
