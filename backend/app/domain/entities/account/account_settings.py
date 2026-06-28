from app.domain.entities.base import TimestampedEntity


class AccountSettingsEntity(TimestampedEntity):
    """Настройки аккаунта (пока — только переключатель уведомлений о расписании)."""

    account_id: int
    schedule_notifications_enabled: bool
