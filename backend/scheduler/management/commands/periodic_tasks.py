import logging

from actuators.services.radiator_synchronization import RadiatorSyncService
from consumption.mutators import save_teleinfo_data
from core.constants import LoggerLabel
from core.services.system_metrics import log_system_metrics
from django.core.management.base import BaseCommand
from heating.services.heating_synchronization import (
    synchronize_room_heating_states_with_radiators,
    synchronize_room_requested_heating_states_with_room_heating_day_plan,
)

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Exécute les tâches périodiques"

    def handle(self, *args, **options):
        label = LoggerLabel.PERIODIC_TASKS
        logger.info(f"{label} save_teleinfo_data: start")
        save_teleinfo_data()
        logger.info(f"{label} save_teleinfo_data: done")

        logger.info(f"{label} sync_requested_heating_states: start")
        synchronize_room_requested_heating_states_with_room_heating_day_plan()
        logger.info(f"{label} sync_requested_heating_states: done")

        logger.info(f"{label} sync_heating_states_with_radiators: start")
        synchronize_room_heating_states_with_radiators()
        logger.info(f"{label} sync_heating_states_with_radiators: done")

        logger.info(f"{label} radiator_hardware_sync: start")
        RadiatorSyncService.synchronize_database_and_hardware()
        logger.info(f"{label} radiator_hardware_sync: done")

        logger.info(f"{label} log_system_metrics: start")
        log_system_metrics()
        logger.info(f"{label} log_system_metrics: done")
