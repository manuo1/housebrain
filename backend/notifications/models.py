from django.db import models


class Notification(models.Model):
    """
    Log of every notification HouseBrain attempted to send, regardless of
    channel. event_code is a free-form string (not a fixed choices list)
    so any app can emit new notification types without touching this app.
    """

    class Level(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Warning"
        CRITICAL = "CRITICAL", "Critical"

    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        SENT = "SENT", "Envoyée"
        FAILED = "FAILED", "Échec"

    event_code = models.CharField(
        max_length=100,
        verbose_name="Événement",
        help_text="Identifiant libre de l'événement à l'origine de la notification.",
    )

    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.INFO,
        verbose_name="Niveau",
    )

    message = models.TextField(
        verbose_name="Message",
    )

    triggered_by_username = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Déclenché par",
        help_text="Username de l'utilisateur authentifié à l'origine de l'action, si applicable.",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créée le",
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Envoyée le",
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.level}] {self.event_code} ({self.status})"
