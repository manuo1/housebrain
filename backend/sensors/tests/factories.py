import factory

from device.tests.factories import SensorTrueFalseFactory
from sensors.models import DoorContactSensor, TemperatureSensor


class TemperatureSensorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TemperatureSensor


class DoorContactSensorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoorContactSensor

    name = factory.Sequence(lambda n: f"Capteur porte {n}")
    sensor_true_false = factory.SubFactory(SensorTrueFalseFactory)
    closed_when_true = True
