from app.app_layer.interfaces.notifications.lesson_notification.dto import (
    LessonNotification,
)


def format_notification(notification: LessonNotification) -> str:
    start_time = notification.lesson_start.strftime("%H:%M")
    subject = notification.lesson.subject
    teacher = notification.lesson.teacher or "Преподаватель не указан"
    if notification.lesson.is_online and notification.lesson.conference_url:
        return (
            f"Пара в {start_time}: {subject} ({teacher})\n"
            f"{notification.lesson.conference_url}"
        )
    return f"Пара в {start_time}: {subject} ({teacher})"
