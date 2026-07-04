from django.utils import timezone
from monitoring.mutators.system_logs import delete_old_system_logs, save_system_logs
from monitoring.services.journalctl_log_collector import collect_journalctl_logs


def collect_and_save_journalctl_system_logs() -> None:
    logs = collect_journalctl_logs()
    save_system_logs(logs)


def cleanup_system_logs_if_needed() -> None:
    """
    Runs the log purge once a day, without needing a dedicated systemd
    timer: this is called every minute (like the rest of periodic_tasks),
    and only actually does something during the 00:00 minute.
    """
    now = timezone.localtime()
    if now.hour == 0 and now.minute == 0:
        delete_old_system_logs()
