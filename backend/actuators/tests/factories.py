import factory
from actuators.models import Radiator


class RadiatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Radiator

    name = factory.Sequence(lambda n: f"Radiateur {n}")
    control_pin = factory.Sequence(lambda n: n % 16)
    power = 10
