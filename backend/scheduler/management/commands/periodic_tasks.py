import logging
from django.core.management.base import BaseCommand

from core.constants import LoggerLabel
from consumption.mutators import save_teleinfo_data

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Exécute les tâches périodiques"

    def handle(self, *args, **options):
        logger.info(f"{LoggerLabel.PERIODIC_TASKS} save_teleinfo_data()")
        save_teleinfo_data()
