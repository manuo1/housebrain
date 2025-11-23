from actuators.models import Radiator
from django.db import models
from sensors.models import TemperatureSensor


class Room(models.Model):
    class HeatingControlMode(models.TextChoices):
        THERMOSTAT = "thermostat", "Piloté par plannings de température"
        ONOFF = "on_off", "Piloté par plannings on/off"

    class RequestedHeatingState(models.TextChoices):
        OFF = "off", "Éteint"
        ON = "on", "Allumé"
        UNKNOWN = "unknown", "Non défini"

    name = models.CharField(max_length=100)

    temperature_sensor = models.ForeignKey(
        TemperatureSensor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Capteur de température",
    )

    radiator = models.ForeignKey(
        Radiator,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Radiateur",
    )

    heating_control_mode = models.CharField(
        max_length=20,
        choices=HeatingControlMode.choices,
        default=HeatingControlMode.ONOFF,
        verbose_name="Mode de pilotage du chauffage",
        help_text="Définit si la pièce est pilotée par consigne de température ou en on/off.",
    )

    temperature_setpoint = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Consigne de température",
        help_text="Température souhaitée lorsque la pièce est pilotée par thermostat (en C°).",
    )

    requested_heating_state = models.CharField(
        max_length=20,
        choices=RequestedHeatingState.choices,
        default=RequestedHeatingState.UNKNOWN,
        verbose_name="Consigne d'état du chauffage",
        help_text="État souhaité du chauffage dans cette pièce.",
    )

    class Meta:
        verbose_name = "Pièce"
        verbose_name_plural = "Pièces"

    def __str__(self):
        return self.name
