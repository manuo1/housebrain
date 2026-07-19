import logging

from core.constants import LoggerLabel
from core.utils.env_utils import environment_is_development

logger = logging.getLogger("django")


def notify_watchdog() -> None:
    """
    Notify the systemd watchdog only in production.
    """
    if not environment_is_development():
        try:
            from systemd import daemon

            daemon.notify("WATCHDOG=1")
        except ImportError as e:
            logger.error(f"{LoggerLabel.SYSTEMD} ImportError: {e}")
