from django.db import models
from django.utils import timezone

from actuators.models import OnOffSwitch, SingleButtonMotor
from equipment.constants import EquipmentStatusLevel
from sensors.models import DoorContactSensor


class Equipment(models.Model):
    """
    Abstract base for any equipment exposed to the user as a home-screen
    card: something with a readable current state and a status level.
    Deliberately doesn't say how many sensors back that state, or how
    it's triggered — e.g. a future roller shutter could combine two limit
    sensors into one get_status() result, with no change needed here.

    get_status() bundles state (text) and status_level (color hint) in a
    single call so a concrete equipment only needs one hardware read per
    card build, even if computing both values requires the same sensor
    read — splitting them into two methods would double the read.

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

    def get_status(self) -> dict:
        """Returns {"state": str, "status_level": EquipmentStatusLevel}."""
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

    # Used by equipment.api.selectors to fetch a full card in one SQL
    # query regardless of the number of equipment rows — without this,
    # each get_readable_state()/trigger() call chases its FK chain with
    # separate queries (N+1).
    select_related_fields = (
        "door_sensor__sensor_true_false__device_io__device",
        "motor__relay_on_off__device_io__device",
    )

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

    def get_status(self) -> dict:
        is_closed = self.door_sensor.is_closed()
        return {
            "state": "Porte fermée" if is_closed else "Porte ouverte",
            "status_level": (
                EquipmentStatusLevel.OK if is_closed else EquipmentStatusLevel.WARNING
            ),
        }


class WaterHeater(Equipment):
    """
    A water heater whose day/night contactor coil is driven by a Shelly
    relay wired in series with the Linky teleinfo signal — turning the
    relay on/off forces HC/HP instead of following the Linky schedule.

    Extends Equipment directly, not SingleButtonEquipment: unlike
    GarageDoor, control here is maintained on/off, not a momentary
    trigger. Wraps actuators.OnOffSwitch (mirrors GarageDoor wrapping
    SingleButtonMotor).
    """

    class RequestedState(models.TextChoices):
        """System intention for water heater state"""

        OFF = "OFF", "Éteint"
        ON = "ON", "Allumé"
        LOAD_SHED = "LOAD_SHED", "Délestage (Éteint)"

    class ActualState(models.TextChoices):
        """Last known hardware state of the water heater's switch"""

        OFF = "OFF", "Éteint"
        ON = "ON", "Allumé"
        UNDEFINED = "UNDEFINED", "Indéterminé"

    interaction_type = "toggle_with_state"

    select_related_fields = ("switch__relay_on_off__device_io__device",)

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")

    switch = models.OneToOneField(
        OnOffSwitch,
        on_delete=models.PROTECT,
        related_name="water_heater",
        verbose_name="Interrupteur",
    )

    requested_state = models.CharField(
        max_length=20,
        choices=RequestedState.choices,
        default=RequestedState.OFF,
        verbose_name="État demandé",
        help_text="État souhaité par le système",
    )

    actual_state = models.CharField(
        max_length=20,
        choices=ActualState.choices,
        default=ActualState.UNDEFINED,
        verbose_name="État réel",
        help_text="État réel du chauffe-eau selon le hardware",
    )

    # NOTE: last_requested is intentionally NOT auto_now, same reasoning
    # as Radiator.last_requested — the service that changes
    # requested_state should set it explicitly.
    last_requested = models.DateTimeField(
        default=timezone.now,
        verbose_name="Dernière demande",
        help_text="Horodatage de la dernière modification de requested_state",
    )

    error = models.TextField(
        null=True,
        blank=True,
        verbose_name="Erreur",
        help_text="Message d'erreur en cas de problème de communication hardware",
    )

    class Meta:
        verbose_name = "Chauffe-eau"
        verbose_name_plural = "Chauffe-eau"

    def __str__(self):
        return self.name

    def turn_on(self) -> None:
        self.switch.turn_on()

    def turn_off(self) -> None:
        self.switch.turn_off()

    def get_status(self) -> dict:
        is_on = self.switch.read_state()
        return {
            "state": "Marche forcée (HC)" if is_on else "Arrêt (HP)",
            "status_level": EquipmentStatusLevel.OK,
        }
