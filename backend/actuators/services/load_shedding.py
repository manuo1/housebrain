from actuators.constants import POWER_SAFETY_MARGIN
from actuators.models import Radiator
from actuators.mutators.radiators import apply_load_shedding_to_radiators
from actuators.selectors.radiators import get_radiators_data_for_load_shedding
from actuators.services.radiator_synchronization import RadiatorSyncService


def manage_load_shedding(available_power: int) -> None:
    """
    Manage load shedding to avoid exceeding the authorized power
    """
    radiators_on = get_radiators_data_for_load_shedding()
    radiators_id_for_load_shedding = select_radiators_for_load_shedding(
        available_power, radiators_on
    )
    apply_load_shedding_to_radiators(radiators_id_for_load_shedding)
    # immediately applies the changes
    RadiatorSyncService.synchronize_database_and_hardware()


def select_radiators_for_load_shedding(
    available_power: int | None, radiators_on: list
) -> list:
    """
    Select the radiators that will be turned off for load shedding depending
    on the importance until the available power becomes sufficient again.

    If available_power is None (teleinfo unavailable), turn off all radiators
    except CRITICAL and HIGH importance.
    """
    if available_power is None:
        return [
            radiator["id"]
            for radiator in radiators_on
            if radiator["importance"]
            not in (Radiator.Importance.CRITICAL, Radiator.Importance.HIGH)
        ]

    power_needed = POWER_SAFETY_MARGIN - available_power
    if power_needed <= 0:
        return []

    radiators_to_turn_off = []
    power_recovered = 0

    for radiator in radiators_on:
        radiators_to_turn_off.append(radiator["id"])
        power_recovered += radiator["power"]
        if power_recovered >= power_needed:
            break

    return radiators_to_turn_off
