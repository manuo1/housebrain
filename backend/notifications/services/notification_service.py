import logging

from django.utils import timezone

from core.constants import LoggerLabel
from notifications.models import Notification
from notifications.services.email_backend import EmailBackend, EmailBackendError

logger = logging.getLogger("django")


class NotificationService:
    """
    Generic entry point for the whole app: any app can call notify() to
    both log a Notification row and attempt delivery, without knowing
    anything about how delivery actually happens (currently email only,
    other channels could be added behind this same call later).
    """

    @staticmethod
    def notify(
        event_code: str,
        message: str,
        level: str = Notification.Level.INFO,
        triggered_by_username: str = "",
    ) -> Notification:
        notification = Notification.objects.create(
            event_code=event_code,
            level=level,
            message=message,
            triggered_by_username=triggered_by_username,
        )

        try:
            EmailBackend.send(subject=f"[HouseBrain] {event_code}", message=message)
        except EmailBackendError as e:
            logger.error(
                f"{LoggerLabel.NOTIFICATIONS} Notification {notification.pk} "
                f"failed - {e}"
            )
            notification.status = Notification.Status.FAILED
        else:
            notification.status = Notification.Status.SENT
            notification.sent_at = timezone.now()

        notification.save(update_fields=["status", "sent_at"])
        return notification
