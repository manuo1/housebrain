import factory

from actuators.tests.factories import SingleButtonMotorFactory
from equipment.models import GarageDoor
from sensors.tests.factories import DoorContactSensorFactory


class GarageDoorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GarageDoor

    name = factory.Sequence(lambda n: f"Porte {n}")
    motor = factory.SubFactory(SingleButtonMotorFactory)
    door_sensor = factory.SubFactory(DoorContactSensorFactory)
