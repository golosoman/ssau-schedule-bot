from enum import StrEnum


class TelegramChatCheckStatus(StrEnum):
    REACHABLE = "reachable"
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"
    FAILED = "failed"

