from monitoring.models import SystemLog


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
