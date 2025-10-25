import logging

from actuators.services.radiator_synchronization import RadiatorSyncService
from consumption.mutators import save_teleinfo_data
from django.core.management.base import BaseCommand
from monitoring.services.log_service import collect_and_save_journalctl_system_logs

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Exécute les tâches périodiques"

    def handle(self, *args, **options):
        save_teleinfo_data()
        RadiatorSyncService.synchronize_database_and_hardware()
        collect_and_save_journalctl_system_logs()
