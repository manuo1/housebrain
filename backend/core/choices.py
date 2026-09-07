from django.db import models


class LoadSheddingImportance(models.IntegerChoices):
    """Shared priority scale for load shedding/turn-on order, used by any
    power-consuming equipment competing for the same available power
    budget (radiators, water heater, ...). Lower value = higher priority
    (shed last, turned on first)."""

    CRITICAL = 0, "Critique"
    HIGH = 1, "Haute"
    MEDIUM = 2, "Moyenne"
    LOW = 3, "Basse"
