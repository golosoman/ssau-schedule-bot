from enum import StrEnum


class TelegramChatCheckStatusEnum(StrEnum):
    REACHABLE = "reachable"
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"
    FAILED = "failed"
