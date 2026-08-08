import factory

from notifications.models import Notification


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    event_code = factory.Sequence(lambda n: f"test_event_{n}")
    level = Notification.Level.INFO
    message = "Test message"
