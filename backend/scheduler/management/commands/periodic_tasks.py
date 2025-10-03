import logging
from django.core.management.base import BaseCommand

from actuators.services.radiator_synchronization import RadiatorSyncService
from consumption.mutators import save_teleinfo_data

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Exécute les tâches périodiques"

    def handle(self, *args, **options):
        save_teleinfo_data()
        RadiatorSyncService.synchronize_database_and_hardware()
