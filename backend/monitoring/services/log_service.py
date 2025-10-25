from monitoring.mutators.system_logs import save_system_logs
from monitoring.services.journalctl_log_collector import collect_journalctl_logs


def collect_and_save_journalctl_system_logs() -> None:
    logs = collect_journalctl_logs()
    save_system_logs(logs)
