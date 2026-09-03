import factory

from actuators.tests.factories import OnOffSwitchFactory, SingleButtonMotorFactory
from equipment.models import GarageDoor, WaterHeater
from sensors.tests.factories import DoorContactSensorFactory


class GarageDoorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GarageDoor

    name = factory.Sequence(lambda n: f"Porte {n}")
    motor = factory.SubFactory(SingleButtonMotorFactory)
    door_sensor = factory.SubFactory(DoorContactSensorFactory)


class WaterHeaterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WaterHeater

    name = factory.Sequence(lambda n: f"Chauffe-eau {n}")
    switch = factory.SubFactory(OnOffSwitchFactory)
