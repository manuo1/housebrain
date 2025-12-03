import json
import logging
import subprocess
from datetime import datetime, timezone

from core.constants import MICROSECONDS_PER_SECOND, LoggerLabel
from django.utils import timezone as django_timezone

logger = logging.getLogger("django")

SERVICES = [
    "bluetooth-listener.service",
    "gunicorn.service",
    "nginx.service",
    "redis-server.service",
    "teleinfo-listener.service",
    "housebrain-periodic.service",
]

PRIORITY_MAP = {
    "0": "EMERGENCY",
    "1": "ALERT",
    "2": "CRITICAL",
    "3": "ERROR",
    "4": "WARNING",
    "5": "NOTICE",
    "6": "INFO",
    "7": "DEBUG",
}


IMPORTANT_KEYWORDS = {
    # technical errors
    "error",
    "fail",
    "failed",
    "exception",
    "traceback",
    "timeout",
    "critical",
    "crash",
    "unreachable",
    "disconnect",
    "killed",
    "panic",
    # startup/service problems
    "restart",
    "restarting",
    "booting",
    "worker",
    "stopped",
    "unhealthy",
    # HTTP error codes
    "400",
    "401",
    "403",
    "404",
    "408",
    "409",
    "500",
    "502",
    "503",
    "504",
    *[label.value.lower() for label in LoggerLabel],
}

# Important: use lowercase
NOT_IMPORTANT_KEYWORDS = {
    ".service: consumed",
    "available power is too low",
}


def is_important_log(message: str) -> bool:
    """
    Keep only logs that contain at least one interesting keyword or code.
    """
    if not message or not isinstance(message, str):
        return False

    msg = message.lower()
    # Case when messages cen contain fake important keyword
    # ex: ".service: Consumed 3.504s CPU time."
    # Message contain 504 but it's not an HTTP error
    if any(keyword in msg for keyword in NOT_IMPORTANT_KEYWORDS):
        return False

    return any(keyword in msg for keyword in IMPORTANT_KEYWORDS)


def get_service_logs(service: str) -> str:
    cmd = ["journalctl", "-u", service, "--since", "2 minutes ago", "-o", "json"]

    try:
        return subprocess.check_output(cmd, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        logger.error(
            f"{LoggerLabel.MONITORING} Timeout while collecting logs from {service}"
        )
        return ""
    except subprocess.CalledProcessError as e:
        logger.warning(
            f"{LoggerLabel.MONITORING} Unable to retrieve logs from {service}: {e}"
        )
        return ""


def parse_json_line(service: str, line: str) -> dict:
    try:
        return json.loads(line)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(
            f"{LoggerLabel.MONITORING} JSON parsing error for {service}: {e} | line: {line}"
        )
        return {}


def get_log_level(service: str, line_data: dict) -> str:
    try:
        log_level = PRIORITY_MAP[str(line_data["PRIORITY"])]
    except (AttributeError, KeyError, TypeError):
        log_level = "UNKNOWN"

    if log_level == "UNKNOWN":
        logger.warning(
            f"{LoggerLabel.MONITORING} Unable to get log level for {service}, entry: {line_data}"
        )

    return log_level


def get_message(service: str, line_data: dict) -> str:
    try:
        message = str(line_data["MESSAGE"])
    except (AttributeError, TypeError, KeyError):
        message = ""
    if not message:
        logger.warning(
            f"{LoggerLabel.MONITORING} Empty MESSAGE field for service {service}, entry: {line_data}"
        )
    return message.strip()


def get_logged_at(service: str, line_data: dict) -> datetime:
    try:
        return django_timezone.localtime(
            datetime.fromtimestamp(
                int(line_data["__REALTIME_TIMESTAMP"]) / MICROSECONDS_PER_SECOND,
                tz=timezone.utc,
            )
        )
    except (KeyError, ValueError, TypeError) as e:
        logger.warning(
            f"{LoggerLabel.MONITORING} Cannot get logged datetime for service {service}, using now(): {e}, entry: {line_data}"
        )
        return django_timezone.now()


def collect_journalctl_logs() -> list[dict]:
    """
    Collects systemd logs from the 5 fixed services over the last 2 minutes.
    """
    logs = []

    for service in SERVICES:
        service_logs = get_service_logs(service)
        if not service_logs:
            continue

        for line in service_logs.strip().splitlines():
            if not line:
                continue

            line_data = parse_json_line(service, line)

            if not line_data:
                continue

            log_level = get_log_level(service, line_data)

            message = get_message(service, line_data)

            if not message or not is_important_log(message):
                continue

            logged_at = get_logged_at(service, line_data)

            logs.append(
                {
                    "service": service,
                    "level": log_level,
                    "message": message,
                    "logged_at": logged_at,
                }
            )

    return logs
