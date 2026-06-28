from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.rest.routers.admin.v1.users.schemas import V1ListAccountsOutputSchema
from app.app_layer.interfaces.use_cases.list_accounts.interface import IListAccountsUseCase
from app.di.container import Container

router = APIRouter(prefix="/users", tags=["Admin"])


@router.get("", response_model=V1ListAccountsOutputSchema)
@inject
async def list_users(
    use_case: Annotated[
        IListAccountsUseCase,
        Depends(Provide[Container.usecases.list_accounts_use_case]),
    ],
) -> V1ListAccountsOutputSchema:
    """Список пользователей системы (без критичных данных)."""
    result = await use_case.execute()
    return V1ListAccountsOutputSchema.from_use_case_dto(result)
