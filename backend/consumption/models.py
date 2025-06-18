from django.db import models


class DailyIndexes(models.Model):
    date = models.DateField(unique=True)
    values = models.JSONField(default=dict)
    tarif_periods = models.JSONField(default=dict)

    def __str__(self):
        return f"Indexes du {self.date}"
