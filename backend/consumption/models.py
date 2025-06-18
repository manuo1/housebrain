from django.db import models


class DailyIndexes(models.Model):
    date = models.DateField(unique=True)
    values = models.JSONField(default=dict)
    tarif_periods = models.JSONField(default=dict)
    subscribed_power = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Indexes du {self.date}"
