from enum import StrEnum


class AuthenticateUserStatusEnum(StrEnum):
    SUCCESS = "success"
    PROFILE_FETCH_ERROR = "profile_fetch_error"
    PROFILE_NOT_FOUND = "profile_not_found"
