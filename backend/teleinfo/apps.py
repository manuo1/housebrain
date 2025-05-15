from django.apps import AppConfig, apps
import logging
import threading
import time
from teleinfo.listener import TeleinfoListener
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger("django")


class TeleinfoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teleinfo"

    def ready(self):
        """
        Start a thread that monitors whether the application is fully ready.
        """

        def wait_for_app_ready():
            while not apps.ready:
                logger.info("Waiting for application to be fully ready...")
                time.sleep(5)
            logger.info("Application is fully ready, starting Teleinfo Listener...")
            teleinfo_listener = TeleinfoListener()
            teleinfo_listener.start_thread()
            cache.set(
                "teleinfo_data", {"created": timezone.now(), "last_saved_at": None}
            )

        # Waiting thread
        threading.Thread(target=wait_for_app_ready, daemon=True).start()
