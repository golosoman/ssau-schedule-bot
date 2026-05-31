import uvicorn

from app.settings.config import settings


def main() -> None:
    uvicorn.run(
        "app.api.rest.app:create_app",
        factory=True,
        host=settings.api.host,
        port=settings.api.port,
        log_level=settings.logging.level.lower(),
    )


if __name__ == "__main__":
    main()
