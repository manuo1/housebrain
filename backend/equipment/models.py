from django.db import models

from actuators.models import Shelly


class PulseSwitch(models.Model):
    """
    A device that only needs a momentary pulse to act — the device itself
    manages the actual movement/state afterwards (e.g. a garage door or
    gate motor). Not for permanent on/off equipment (e.g. a lamp), which
    would need a different model with its own semantics.
    """

    class Status(models.TextChoices):
        IDLE = "IDLE", "Idle"
        IN_PROGRESS = "IN_PROGRESS", "In progress"

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
    )

    shelly = models.ForeignKey(
        Shelly,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Shelly",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IDLE,
        verbose_name="Statut",
        help_text="Verrou applicatif contre les déclenchements concurrents.",
    )

    last_triggered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernier déclenchement",
    )

    class Meta:
        verbose_name = "Interrupteur à impulsion"
        verbose_name_plural = "Interrupteurs à impulsion"

    def __str__(self):
        return self.name
