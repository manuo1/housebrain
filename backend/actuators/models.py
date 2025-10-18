from django.db import models
from django.utils import timezone


class Radiator(models.Model):
    class Importance(models.IntegerChoices):
        """Heating importance level (higher importance = use last for load shedding)"""

        CRITICAL = 0, "Critique"
        HIGH = 1, "Haute"
        MEDIUM = 2, "Moyenne"
        LOW = 3, "Basse"

    class RequestedState(models.TextChoices):
        """System intention for radiator state"""

        OFF = "OFF", "Éteint"
        ON = "ON", "Allumé"
        LOAD_SHED = "LOAD_SHED", "Délestage (Éteint)"

    class ActualState(models.TextChoices):
        """Last known hardware state of radiator"""

        OFF = "OFF", "Éteint"
        ON = "ON", "Allumé"
        UNDEFINED = "UNDEFINED", "Indéterminé"
        # see actuators\mappers.py

    # Hardware pin choices for MCP23017 (16 pins: 0-15)
    MCP23017_PIN_CHOICES = [(pin, f"Pin {pin}") for pin in range(16)]

    # Basic radiator information
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
        help_text="Nom du radiateur",
    )

    power = models.PositiveIntegerField(
        verbose_name="Puissance (W)",
        help_text="Puissance électrique du radiateur en watts",
    )

    control_pin = models.PositiveSmallIntegerField(
        choices=MCP23017_PIN_CHOICES,
        unique=True,
        verbose_name="Pin MCP23017",
        help_text="Pin du MCP23017 contrôlant ce radiateur (0-15)",
    )

    importance = models.PositiveSmallIntegerField(
        choices=Importance.choices,
        default=Importance.MEDIUM,
        verbose_name="Importance du chauffage",
        help_text="Détermine l'ordre de délestage (critique = coupé en dernier)",
    )

    # State management
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
        help_text="État réel du radiateur selon le hardware",
    )

    # Timestamps for traceability
    # NOTE: last_requested is intentionally NOT auto_now to allow manual control
    # from services. Services should explicitly update this field when changing
    # requested_state to maintain accurate traceability of system decisions.
    last_requested = models.DateTimeField(
        default=timezone.now(),
        verbose_name="Dernière demande",
        help_text="Horodatage de la dernière modification de requested_state",
    )

    # Error tracking
    error = models.TextField(
        null=True,
        blank=True,
        verbose_name="Erreur",
        help_text="Message d'erreur en cas de problème de communication hardware",
    )

    class Meta:
        verbose_name = "Radiateur"
        verbose_name_plural = "Radiateurs"

    def __str__(self):
        last_req = timezone.localtime(self.last_requested).strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"{self.name} | "
            f"Actual: {self.get_actual_state_display()} | "
            f"Requested: {self.get_requested_state_display()} @ {last_req}"
        )
