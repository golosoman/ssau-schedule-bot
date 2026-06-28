import logging
from typing import TYPE_CHECKING

from app.logging.filters import LoggingContextFilter, RedactingFilter, SQLAlchemyErrorFilter
from app.logging.formatters import JsonFormatter

if TYPE_CHECKING:
    from app.settings.config import Settings

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
NOISY_LOGGERS = ("httpx", "httpcore", "aiohttp", "aiogram")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def configure_logging(settings: "Settings") -> None:
    level = _parse_level(settings.logging.level)
    handler = logging.StreamHandler()

    if settings.logging.format.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt=DEFAULT_LOG_FORMAT,
                datefmt=DEFAULT_DATE_FORMAT,
            )
        )

    handler.addFilter(LoggingContextFilter())
    handler.addFilter(SQLAlchemyErrorFilter())
    handler.addFilter(RedactingFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)

    for logger_name in NOISY_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def _parse_level(level_name: str) -> int:
    normalized = level_name.upper()
    level = logging.getLevelName(normalized)
    if isinstance(level, int):
        return level
    return logging.INFO
