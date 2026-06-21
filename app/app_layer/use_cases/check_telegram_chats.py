from collections.abc import Callable

from app.app_layer.interfaces.repos.account.interface import IAccountRepository
from app.app_layer.interfaces.telegram.chat_checker.dto import TelegramChatCheckResult
from app.app_layer.interfaces.telegram.chat_checker.enums import TelegramChatCheckStatus
from app.app_layer.interfaces.telegram.chat_checker.interface import ITelegramChatChecker
from app.app_layer.interfaces.uow.unit_of_work.interface import IUnitOfWork
from app.app_layer.interfaces.use_cases.check_telegram_chats.dto.input import (
    CheckTelegramChatsUseCaseInputDTO,
)
from app.app_layer.interfaces.use_cases.check_telegram_chats.dto.output import (
    CheckTelegramChatsUseCaseOutputDTO,
)
from app.app_layer.interfaces.use_cases.check_telegram_chats.interface import (
    ICheckTelegramChatsUseCase,
)


class CheckTelegramChatsUseCase(ICheckTelegramChatsUseCase):
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        account_repo: IAccountRepository,
        chat_checker: ITelegramChatChecker,
    ) -> None:
        self._uow_factory = uow_factory
        self._account_repo = account_repo
        self._chat_checker = chat_checker

    async def execute(
        self,
        input_dto: CheckTelegramChatsUseCaseInputDTO,
    ) -> CheckTelegramChatsUseCaseOutputDTO:
        chat_ids = input_dto.chat_ids
        if chat_ids is None:
            chat_ids = await self._load_known_chat_ids()

        unique_chat_ids = _deduplicate(chat_ids)
        checked: list[TelegramChatCheckResult] = []
        for chat_id in unique_chat_ids:
            checked.append(await self._chat_checker.check(chat_id))

        return CheckTelegramChatsUseCaseOutputDTO(
            checked=checked,
            total=len(checked),
            reachable=_count_status(checked, TelegramChatCheckStatus.REACHABLE),
            not_found=_count_status(checked, TelegramChatCheckStatus.NOT_FOUND),
            forbidden=_count_status(checked, TelegramChatCheckStatus.FORBIDDEN),
            failed=_count_status(checked, TelegramChatCheckStatus.FAILED),
            skipped=len(chat_ids) - len(unique_chat_ids),
        )

    async def _load_known_chat_ids(self) -> list[int]:
        async with self._uow_factory():
            accounts = await self._account_repo.list_all()
        return [account.chat_id for account in accounts]


def _deduplicate(chat_ids: list[int]) -> list[int]:
    seen: set[int] = set()
    result: list[int] = []
    for chat_id in chat_ids:
        if chat_id in seen:
            continue
        seen.add(chat_id)
        result.append(chat_id)
    return result


def _count_status(
    results: list[TelegramChatCheckResult],
    status: TelegramChatCheckStatus,
) -> int:
    return sum(1 for result in results if result.status == status)
