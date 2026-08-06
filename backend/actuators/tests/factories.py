import factory

from actuators.models import Radiator, Shelly


class RadiatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Radiator

    name = factory.Sequence(lambda n: f"Radiateur {n}")
    control_pin = factory.Sequence(lambda n: n % 16)
    power = 10


class ShellyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shelly

    name = factory.Sequence(lambda n: f"Shelly {n}")
    reference = Shelly.Reference.SHELLY_1_MINI_GEN3
    ip = factory.Sequence(lambda n: f"192.168.1.{n % 254 + 1}")
