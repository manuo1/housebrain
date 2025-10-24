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

NOT_CRITICAL_LEVELS = {"INFO", "DEBUG"}


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


def collect_logs() -> list[dict]:
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

            if log_level in NOT_CRITICAL_LEVELS:
                continue

            message = get_message(service, line_data)

            if not message:
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
