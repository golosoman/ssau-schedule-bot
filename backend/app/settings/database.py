from pydantic import BaseModel, ConfigDict


class DatabaseSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str = "sqlite+aiosqlite:///./data/ssau_schedule_bot.db"
