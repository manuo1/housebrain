from datetime import timedelta

from django.utils import timezone
from monitoring.models import SystemLog

# Retention: critical entries are kept longer since they're the ones worth
# cross-referencing with a future crash. Routine/low-severity entries are
# pure noise once they age out.
CRITICAL_LEVELS = ["EMERGENCY", "ALERT", "CRITICAL", "ERROR"]
CRITICAL_LEVELS_RETENTION_DAYS = 90
OTHER_LEVELS_RETENTION_DAYS = 14


def save_system_logs(logs: list[dict]) -> int:
    if not logs:
        return
    log_objects = [
        SystemLog(
            service=log["service"],
            level=log["level"],
            message=log["message"],
            logged_at=log["logged_at"],
        )
        for log in logs
    ]
    SystemLog.objects.bulk_create(log_objects, ignore_conflicts=True)


def delete_old_system_logs() -> None:
    """Deletes system logs past their retention period, based on level."""
    now = timezone.now()

    SystemLog.objects.filter(
        level__in=CRITICAL_LEVELS,
        logged_at__lt=now - timedelta(days=CRITICAL_LEVELS_RETENTION_DAYS),
    ).delete()

    SystemLog.objects.exclude(level__in=CRITICAL_LEVELS).filter(
        logged_at__lt=now - timedelta(days=OTHER_LEVELS_RETENTION_DAYS),
    ).delete()
