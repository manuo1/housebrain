import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Exécute les tâches périodiques"

    def handle(self, *args, **options):

        pass
