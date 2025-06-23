import logging
from django.core.management.base import BaseCommand

from consumption.mutators import save_teleinfo_data

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Exécute les tâches périodiques"

    def handle(self, *args, **options):
        save_teleinfo_data()
