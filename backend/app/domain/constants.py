from enum import IntEnum


class SubgroupValueEnum(IntEnum):
    ALL = 0
    ONE = 1
    TWO = 2


DEFAULT_SUBGROUP_VALUE = SubgroupValueEnum.ALL
DEFAULT_USER_TYPE = "student"
DAYS_IN_WEEK = 7
TELEGRAM_MESSAGE_MAX_LENGTH = 4096
