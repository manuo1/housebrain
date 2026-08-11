from django.db import models

from actuators.models import SingleButtonMotor
from sensors.models import DoorContactSensor


class Equipment(models.Model):
    """
    Abstract base for any equipment exposed to the user as a home-screen
    card: something with a readable current state. Deliberately doesn't
    say how many sensors back that state, or how it's triggered — e.g. a
    future roller shutter could combine two limit sensors into one
    get_readable_state() string, with no change needed here.

    `interaction_type` is a class attribute (fixed per concrete type, not
    a DB field — an instance never changes how it's meant to be
    interacted with) meant to be read by a future aggregation
    service/registry to group equipment by front-end interaction pattern
    (e.g. "long_press_with_state"). No registry yet — see chat notes,
    comes once a second concrete type exists to validate the pattern.
    """

    interaction_type: str

    class Meta:
        abstract = True

    def get_readable_state(self) -> str:
        raise NotImplementedError


class SingleButtonEquipment(Equipment):
    """
    Equipment interacted with via a single momentary action (e.g. a
    front-end long-press) — as opposed to e.g. a roller shutter with
    separate up()/down() actions, which would extend Equipment directly
    instead.
    """

    class Meta:
        abstract = True

    def trigger(self) -> None:
        raise NotImplementedError


class GarageDoor(SingleButtonEquipment):
    interaction_type = "long_press_with_state"

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")

    motor = models.OneToOneField(
        SingleButtonMotor,
        on_delete=models.PROTECT,
        related_name="garage_door",
        verbose_name="Moteur",
    )

    door_sensor = models.OneToOneField(
        DoorContactSensor,
        on_delete=models.PROTECT,
        related_name="garage_door",
        verbose_name="Capteur",
    )

    class Meta:
        verbose_name = "Porte de garage"
        verbose_name_plural = "Portes de garage"

    def __str__(self):
        return self.name

    def trigger(self) -> None:
        self.motor.trigger()

    def get_readable_state(self) -> str:
        return self.door_sensor.get_readable_state()
