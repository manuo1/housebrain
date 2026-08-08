import logging

from django.conf import settings
from django.core.mail import send_mail

from core.constants import LoggerLabel

logger = logging.getLogger("django")


class EmailBackendError(Exception):
    """Exception for EmailBackend errors"""


class EmailBackend:
    """
    Thin wrapper around Django's send_mail, using notification-specific
    SMTP settings (independent from any other email use HouseBrain might
    add later). Only one recipient exists today (Emmanuel himself), but
    the backend takes it from settings rather than hardcoding it here.
    """

    @staticmethod
    def send(subject: str, message: str) -> None:
        recipient = settings.NOTIFICATIONS_EMAIL_RECIPIENT
        if not recipient:
            raise EmailBackendError("NOTIFICATIONS_EMAIL_RECIPIENT is not configured")

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.NOTIFICATIONS_EMAIL_USER,
                recipient_list=[recipient],
            )
        except Exception as e:
            logger.error(f"{LoggerLabel.NOTIFICATIONS} Unable to send email - {e}")
            raise EmailBackendError(f"Unable to send email: {e}")
