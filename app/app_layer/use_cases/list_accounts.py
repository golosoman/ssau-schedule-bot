from collections.abc import Callable

from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.app_layer.interfaces.use_cases.list_accounts.dto.output import (
    ListAccountsUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.list_accounts.interface import IListAccountsUseCase


class ListAccountsUseCase(IListAccountsUseCase):
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        account_repo: IAccountRepository,
    ) -> None:
        self._uow_factory = uow_factory
        self._account_repo = account_repo

    async def execute(self) -> ListAccountsUseCaseOutputDTO:
        async with self._uow_factory():
            accounts = await self._account_repo.list_all()
        return ListAccountsUseCaseOutputDTO(accounts=accounts)
