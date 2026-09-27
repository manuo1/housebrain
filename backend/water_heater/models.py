from django.db import models

from equipment.models import WaterHeater
from planning.models import EquipmentDayPlan


class WaterHeaterDayPlan(EquipmentDayPlan):
    """
    Daily on/off plan for a specific water heater.
    Links a water heater to a schedule pattern for a specific date.
    Mirrors heating.RoomHeatingDayPlan. date/schedule_pattern come from
    EquipmentDayPlan.
    """

    equipment = models.ForeignKey(
        WaterHeater,
        on_delete=models.CASCADE,
        related_name="day_plans",
        verbose_name="Chauffe-eau",
    )

    class Meta:
        verbose_name = "Plan de chauffe-eau journalier"
        verbose_name_plural = "Plans de chauffe-eau journaliers"
        # One plan per water heater per day
        unique_together = [["equipment", "date"]]
        ordering = ["date", "equipment"]

    def __str__(self):
        return f"{self.equipment.name} - {self.date}"
