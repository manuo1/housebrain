from django.db import models


class DailyConsumption(models.Model):
    date = models.DateField(unique=True)
    values = models.JSONField(default=dict)

    def __str__(self):
        return f"Consommation du {self.date}"
