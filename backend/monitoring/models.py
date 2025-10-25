from django.db import models


class SystemLog(models.Model):
    service = models.CharField(max_length=100)
    level = models.CharField(max_length=20)
    message = models.TextField()
    logged_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-logged_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["service", "logged_at", "level", "message"],
                name="unique_system_log",
            )
        ]

    def __str__(self):
        return (
            f"{self.service} - {self.level} - {self.logged_at} - {self.message[:100]}"
        )
