from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseEngineSettings:
    url: str
    echo: bool = False
