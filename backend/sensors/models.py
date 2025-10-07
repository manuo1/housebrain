from django.db import models


class TemperatureSensor(models.Model):
    name = models.CharField(max_length=100)
    mac_address = models.CharField(max_length=17, unique=True)

    class Meta:
        verbose_name = "Capteur de température"
        verbose_name_plural = "Capteurs de température"

    def __str__(self):
        return f"{self.mac_address} - {self.name}"
