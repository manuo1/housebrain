from django.db import models

from planning.models import SchedulePattern
from rooms.models import Room


class RoomHeatingDayPlan(models.Model):
    """
    Daily heating plan for a specific room.
    Links a room to a schedule pattern for a specific date.
    """

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="heating_day_plans",
        verbose_name="Pièce",
    )

    date = models.DateField(verbose_name="Date")

    heating_pattern = models.ForeignKey(
        SchedulePattern,
        on_delete=models.PROTECT,
        related_name="day_plans",
        verbose_name="Pattern de chauffage",
        help_text="Programme de chauffage appliqué pour cette journée",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan de chauffage journalier"
        verbose_name_plural = "Plans de chauffage journaliers"
        # One plan per room per day
        unique_together = [["room", "date"]]
        ordering = ["date", "room"]

    def __str__(self):
        return f"{self.room.name} - {self.date}"
