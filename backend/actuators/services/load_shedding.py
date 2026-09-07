from actuators.mutators.radiators import apply_load_shedding_to_radiators
from actuators.selectors.radiators import get_radiators_data_for_load_shedding
from actuators.services.radiator_synchronization import RadiatorSyncService
from core.utils.energy_utils import select_items_for_load_shedding


def manage_load_shedding(remaining_power: int | None) -> None:
    """
    Manage load shedding to avoid exceeding the authorized power
    """

    radiators_on = get_radiators_data_for_load_shedding()
    radiators_id_for_load_shedding = select_items_for_load_shedding(
        remaining_power, radiators_on
    )
    apply_load_shedding_to_radiators(radiators_id_for_load_shedding)
    # immediately applies the changes
    RadiatorSyncService.synchronize_database_and_hardware()
