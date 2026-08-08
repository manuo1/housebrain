import pytest

from notifications.models import Notification
from notifications.services.email_backend import EmailBackendError
from notifications.services.notification_service import NotificationService


@pytest.mark.django_db
def test_notify_success(mocker):
    mock_send = mocker.patch(
        "notifications.services.notification_service.EmailBackend.send"
    )

    notification = NotificationService.notify(
        event_code="garage_door_opened",
        message="La porte du garage a été ouverte.",
        level=Notification.Level.WARNING,
        triggered_by_username="manuo",
    )

    mock_send.assert_called_once_with(
        subject="[HouseBrain] garage_door_opened",
        message="La porte du garage a été ouverte.",
    )
    notification.refresh_from_db()
    assert notification.status == Notification.Status.SENT
    assert notification.sent_at is not None
    assert notification.level == Notification.Level.WARNING
    assert notification.triggered_by_username == "manuo"


@pytest.mark.django_db
def test_notify_default_level_and_no_triggered_by(mocker):
    mocker.patch("notifications.services.notification_service.EmailBackend.send")

    notification = NotificationService.notify(
        event_code="linky_data_loss",
        message="Perte de données Linky.",
    )

    assert notification.level == Notification.Level.INFO
    assert notification.triggered_by_username == ""


@pytest.mark.django_db
def test_notify_email_failure_still_creates_notification_as_failed(mocker):
    mocker.patch(
        "notifications.services.notification_service.EmailBackend.send",
        side_effect=EmailBackendError("smtp boom"),
    )

    notification = NotificationService.notify(
        event_code="garage_door_opened",
        message="La porte du garage a été ouverte.",
    )

    notification.refresh_from_db()
    assert notification.status == Notification.Status.FAILED
    assert notification.sent_at is None
    # the row itself must survive even though delivery failed
    assert Notification.objects.filter(pk=notification.pk).exists()
