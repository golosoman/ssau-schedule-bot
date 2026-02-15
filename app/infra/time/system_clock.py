from datetime import datetime, timezone

from app.app_layer.interfaces.time.clock.interface import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
