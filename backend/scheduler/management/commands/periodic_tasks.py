import logging

from django.core.management.base import BaseCommand

from consumption.mutators import save_teleinfo_data
from core.constants import LoggerLabel
from core.services.system_metrics import log_system_metrics
from heating.services.heating_synchronization import (
    queue_radiators_to_turn_on,
    resolve_radiators_to_update,
    synchronize_room_requested_heating_states_with_room_heating_day_plan,
    turn_off_radiators_and_apply_to_hardware,
)
from water_heater.selectors import get_water_heaters_plan_states
from water_heater.services.water_heater_synchronization import (
    queue_water_heaters_to_turn_on,
    resolve_water_heaters_to_update,
    turn_off_water_heaters_and_apply_to_hardware,
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
        radiators_to_update = resolve_radiators_to_update()
        turn_off_radiators_and_apply_to_hardware(radiators_to_update)
        queue_radiators_to_turn_on(radiators_to_update)
        logger.info(f"{label} sync_heating_states_with_radiators: done")

        logger.info(f"{label} sync_water_heater_states: start")
        water_heaters_plan_states = get_water_heaters_plan_states()
        water_heaters_to_update = resolve_water_heaters_to_update(
            water_heaters_plan_states
        )
        turn_off_water_heaters_and_apply_to_hardware(water_heaters_to_update)
        queue_water_heaters_to_turn_on(water_heaters_to_update)
        logger.info(f"{label} sync_water_heater_states: done")

        logger.info(f"{label} log_system_metrics: start")
        log_system_metrics()
        logger.info(f"{label} log_system_metrics: done")
