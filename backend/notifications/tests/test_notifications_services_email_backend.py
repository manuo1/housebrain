import pytest
from django.test import override_settings

from notifications.services.email_backend import EmailBackend, EmailBackendError


@pytest.mark.django_db
@override_settings(NOTIFICATIONS_EMAIL_RECIPIENT="recipient@example.com")
def test_send_success(mocker):
    mock_send_mail = mocker.patch("notifications.services.email_backend.send_mail")

    EmailBackend.send(subject="Subject", message="Body")

    mock_send_mail.assert_called_once()
    _, kwargs = mock_send_mail.call_args
    assert kwargs["subject"] == "Subject"
    assert kwargs["message"] == "Body"
    assert kwargs["recipient_list"] == ["recipient@example.com"]


@pytest.mark.django_db
@override_settings(NOTIFICATIONS_EMAIL_RECIPIENT="")
def test_send_no_recipient_configured_raises_and_never_calls_send_mail(mocker):
    mock_send_mail = mocker.patch("notifications.services.email_backend.send_mail")

    with pytest.raises(EmailBackendError, match="not configured"):
        EmailBackend.send(subject="Subject", message="Body")

    mock_send_mail.assert_not_called()


@pytest.mark.django_db
@override_settings(NOTIFICATIONS_EMAIL_RECIPIENT="recipient@example.com")
def test_send_smtp_error_raises_email_backend_error(mocker):
    mocker.patch(
        "notifications.services.email_backend.send_mail",
        side_effect=Exception("smtp boom"),
    )

    with pytest.raises(EmailBackendError, match="Unable to send email"):
        EmailBackend.send(subject="Subject", message="Body")
