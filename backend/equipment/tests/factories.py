import factory

from actuators.tests.factories import ShellyFactory
from equipment.models import PulseSwitch


class PulseSwitchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PulseSwitch

    name = factory.Sequence(lambda n: f"Pulse Switch {n}")
    shelly = factory.SubFactory(ShellyFactory)
