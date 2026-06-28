from dataclasses import dataclass


@dataclass(frozen=True)
class SSAUClientSettings:
    base_url: str
    timeout_seconds: float


@dataclass(frozen=True)
class AuthCacheSettings:
    ttl_seconds: int
    min_login_interval_seconds: int
