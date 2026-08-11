import factory

from actuators.models import Radiator, SingleButtonMotor
from device.tests.factories import RelayOnOffFactory


class RadiatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Radiator

    name = factory.Sequence(lambda n: f"Radiateur {n}")
    control_pin = factory.Sequence(lambda n: n % 16)
    power = 10


class SingleButtonMotorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SingleButtonMotor

    name = factory.Sequence(lambda n: f"Moteur {n}")
    relay_on_off = factory.SubFactory(RelayOnOffFactory)
    pulse_seconds = 1
