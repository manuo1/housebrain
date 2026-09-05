from django.db import models

from equipment.models import WaterHeater
from planning.models import SchedulePattern


class WaterHeaterDayPlan(models.Model):
    """
    Daily on/off plan for a specific water heater.
    Links a water heater to a schedule pattern for a specific date.
    Mirrors heating.RoomHeatingDayPlan.
    """

    water_heater = models.ForeignKey(
        WaterHeater,
        on_delete=models.CASCADE,
        related_name="day_plans",
        verbose_name="Chauffe-eau",
    )

    date = models.DateField(verbose_name="Date")

    schedule_pattern = models.ForeignKey(
        SchedulePattern,
        on_delete=models.PROTECT,
        related_name="water_heater_day_plans",
        verbose_name="Pattern de planification",
        help_text="Programme appliqué pour cette journée",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan de chauffe-eau journalier"
        verbose_name_plural = "Plans de chauffe-eau journaliers"
        # One plan per water heater per day
        unique_together = [["water_heater", "date"]]
        ordering = ["date", "water_heater"]

    def __str__(self):
        return f"{self.water_heater.name} - {self.date}"
