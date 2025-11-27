import factory
from sensors.models import TemperatureSensor


class TemperatureSensorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TemperatureSensor
