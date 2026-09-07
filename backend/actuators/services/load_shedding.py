from actuators.mutators.radiators import apply_load_shedding_to_radiators
from actuators.selectors.radiators import get_radiators_data_for_load_shedding
from actuators.services.radiator_synchronization import RadiatorSyncService
from core.utils.energy_utils import select_items_for_load_shedding
from water_heater.mutators import apply_load_shedding_to_water_heaters
from water_heater.selectors import get_water_heaters_data_for_load_shedding
from water_heater.services.water_heater_synchronization import WaterHeaterSyncService


def manage_load_shedding(remaining_power: int | None) -> None:
    """
    Manage load shedding to avoid exceeding the authorized power.

    Radiators are shed first; water heaters are only touched if that
    isn't enough to recover the deficit — water heaters are always kept
    on in priority over heating.
    """

    radiators_on = get_radiators_data_for_load_shedding()
    radiators_id_for_load_shedding = select_items_for_load_shedding(
        remaining_power, radiators_on
    )
    apply_load_shedding_to_radiators(radiators_id_for_load_shedding)
    # immediately applies the changes
    RadiatorSyncService.synchronize_database_and_hardware()

    remaining_power_after_radiators = remaining_power
    if remaining_power is not None:
        power_recovered_from_radiators = sum(
            radiator["power"]
            for radiator in radiators_on
            if radiator["id"] in radiators_id_for_load_shedding
        )
        remaining_power_after_radiators = (
            remaining_power + power_recovered_from_radiators
        )

    water_heaters_on = get_water_heaters_data_for_load_shedding()
    water_heaters_id_for_load_shedding = select_items_for_load_shedding(
        remaining_power_after_radiators, water_heaters_on
    )
    apply_load_shedding_to_water_heaters(water_heaters_id_for_load_shedding)
    WaterHeaterSyncService.synchronize_database_and_hardware()
