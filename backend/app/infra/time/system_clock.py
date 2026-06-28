from datetime import UTC, datetime

from app.app_layer.interfaces.time.clock.interface import IClock


class SystemClock(IClock):
    def now(self) -> datetime:
        return datetime.now(UTC)
