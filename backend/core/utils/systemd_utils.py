import logging
import os

from core.constants import LoggerLabel

logger = logging.getLogger("django")


def notify_watchdog() -> None:
    """
    Notify the systemd watchdog only in production.
    """
    if os.environ["ENVIRONMENT"] == "production":
        try:
            from systemd import daemon

            daemon.notify("WATCHDOG=1")
        except ImportError as e:
            logger.error(f"{LoggerLabel.SYSTEMD} ImportError: {e}")
