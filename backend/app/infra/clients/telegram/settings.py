from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramClientSettings:
    bot_token: str
    proxy_url: str | None = None
