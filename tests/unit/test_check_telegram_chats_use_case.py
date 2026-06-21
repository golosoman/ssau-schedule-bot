import asyncio

from app.app_layer.interfaces.telegram.chat_checker.dto import TelegramChatCheckResult
from app.app_layer.interfaces.telegram.chat_checker.enums import TelegramChatCheckStatus
from app.app_layer.interfaces.use_cases.check_telegram_chats.dto.input import (
    CheckTelegramChatsUseCaseInputDTO,
)
from app.app_layer.use_cases.check_telegram_chats import CheckTelegramChatsUseCase


class FakeAccount:
    def __init__(self, chat_id: int) -> None:
        self.chat_id = chat_id


class FakeAccountRepository:
    def __init__(self, chat_ids: list[int]) -> None:
        self._chat_ids = chat_ids
        self.list_all_called = False

    async def list_all(self) -> list[FakeAccount]:
        self.list_all_called = True
        return [FakeAccount(chat_id) for chat_id in self._chat_ids]


class FakeTelegramChatChecker:
    def __init__(self, statuses: dict[int, TelegramChatCheckStatus]) -> None:
        self._statuses = statuses
        self.checked: list[int] = []

    async def check(self, chat_id: int) -> TelegramChatCheckResult:
        self.checked.append(chat_id)
        return TelegramChatCheckResult(
            chat_id=chat_id,
            status=self._statuses.get(chat_id, TelegramChatCheckStatus.REACHABLE),
        )


class FakeUnitOfWork:
    async def __aenter__(self) -> None:
        return None

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


def _uow_factory() -> FakeUnitOfWork:
    return FakeUnitOfWork()


def test_check_telegram_chats_deduplicates_input_and_builds_summary() -> None:
    async def _run() -> None:
        account_repo = FakeAccountRepository(chat_ids=[])
        checker = FakeTelegramChatChecker(
            statuses={
                2: TelegramChatCheckStatus.NOT_FOUND,
                3: TelegramChatCheckStatus.FORBIDDEN,
                4: TelegramChatCheckStatus.FAILED,
            }
        )
        use_case = CheckTelegramChatsUseCase(
            uow_factory=_uow_factory,
            account_repo=account_repo,
            chat_checker=checker,
        )

        result = await use_case.execute(
            CheckTelegramChatsUseCaseInputDTO(chat_ids=[1, 2, 2, 3, 4])
        )

        assert checker.checked == [1, 2, 3, 4]
        assert account_repo.list_all_called is False
        assert result.total == 4
        assert result.reachable == 1
        assert result.not_found == 1
        assert result.forbidden == 1
        assert result.failed == 1
        assert result.skipped == 1

    asyncio.run(_run())


def test_check_telegram_chats_uses_known_accounts_when_input_is_missing() -> None:
    async def _run() -> None:
        account_repo = FakeAccountRepository(chat_ids=[10, 20, 20])
        checker = FakeTelegramChatChecker(statuses={})
        use_case = CheckTelegramChatsUseCase(
            uow_factory=_uow_factory,
            account_repo=account_repo,
            chat_checker=checker,
        )

        result = await use_case.execute(CheckTelegramChatsUseCaseInputDTO())

        assert account_repo.list_all_called is True
        assert checker.checked == [10, 20]
        assert result.total == 2
        assert result.reachable == 2
        assert result.skipped == 1

    asyncio.run(_run())
