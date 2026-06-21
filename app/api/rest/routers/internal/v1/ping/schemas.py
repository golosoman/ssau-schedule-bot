from pydantic import BaseModel, ConfigDict


class V1PingOutputSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
