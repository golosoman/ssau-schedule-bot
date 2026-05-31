from pydantic import BaseModel, ConfigDict


class ApiSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    host: str = "0.0.0.0"
    port: int = 8080
