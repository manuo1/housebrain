from django.db import models

from device.models import SensorTrueFalse


class TemperatureSensor(models.Model):
    name = models.CharField(max_length=100)
    mac_address = models.CharField(max_length=17, unique=True)

    class Meta:
        verbose_name = "Capteur de température"
        verbose_name_plural = "Capteurs de température"

    def __str__(self):
        return f"{self.mac_address} - {self.name}"


class DoorContactSensor(models.Model):
    """
    A magnetic contact sensor (reed switch) reporting whether a door is
    closed. Wraps a device.SensorTrueFalse and interprets its raw boolean
    according to closed_when_true, so the wiring's actual polarity never
    leaks to callers.
    """

    sensor_true_false = models.OneToOneField(
        SensorTrueFalse,
        on_delete=models.CASCADE,
        related_name="door_contact_sensor",
        verbose_name="Capteur",
    )

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")

    closed_when_true = models.BooleanField(
        default=True,
        verbose_name="Fermée quand vrai",
        help_text=(
            "Coché si la porte est fermée quand l'état brut du capteur est vrai "
            "(décoché si c'est l'inverse)"
        ),
    )

    class Meta:
        verbose_name = "Capteur de porte"
        verbose_name_plural = "Capteurs de porte"

    def __str__(self):
        return self.name

    def is_closed(self) -> bool:
        raw = self.sensor_true_false.read_state()
        return raw if self.closed_when_true else not raw
