import logging

from actuators.mutators.radiators import (
    apply_load_shedding_to_radiators,
    set_radiators_requested_state_to_off,
    set_radiators_requested_state_to_on,
)
from heating.mappers import radiator_state_matches_room_state
from heating.utils.cache_radiators import (
    get_radiators_to_turn_on_in_cache,
    set_radiators_to_turn_on_in_cache,
)
from rooms.models import Room
from rooms.selectors.heating import get_rooms_with_on_off_heating_control_data
from teleinfo.utils.cache_teleinfo_data import get_instant_available_power

logger = logging.getLogger("django")


def get_radiators_to_update_for_on_off_heating_control(rooms_data: list[dict]) -> list:
    radiators = {"to_turn_on": [], "ids_to_turn_off": []}
    for room in rooms_data:
        radiator_state = room["radiator__requested_state"]
        room_state = room["requested_heating_state"]
        if radiator_state is None:
            continue

        if not radiator_state_matches_room_state(room_state, radiator_state):
            match room_state:
                case Room.RequestedHeatingState.ON:
                    radiators["to_turn_on"].append(
                        {
                            "id": room["radiator__id"],
                            "power": room["radiator__power"],
                            "importance": room["radiator__importance"],
                        }
                    )
                case Room.RequestedHeatingState.OFF:
                    radiators["ids_to_turn_off"].append(room["radiator__id"])
                case _:
                    continue

    return radiators


def split_radiators_by_available_power(radiators: list):
    can_turn_on = []
    cannot_turn_on = []
    remaining_power = get_instant_available_power()

    for radiator in radiators:
        if remaining_power >= radiator["power"]:
            can_turn_on.append(radiator)
            remaining_power -= radiator["power"]
        else:
            cannot_turn_on.append(radiator)

    return can_turn_on, cannot_turn_on


def turn_on_radiators_according_to_the_available_power():
    radiators = get_radiators_to_turn_on_in_cache()
    if not radiators:
        return
    sorted_radiators = sorted(radiators, key=lambda x: (x["importance"], -x["power"]))
    can_turn_on, cannot_turn_on = split_radiators_by_available_power(sorted_radiators)

    # Keep the radiators that couldn't be turned on in the cache to try again.
    set_radiators_to_turn_on_in_cache(cannot_turn_on)
    # Turn on the radiators that can.
    set_radiators_requested_state_to_on([radiator["id"] for radiator in can_turn_on])
    # Indicates that the others are experiencing load shedding.
    apply_load_shedding_to_radiators([radiator["id"] for radiator in cannot_turn_on])


def synchronize_heating_for_rooms_with_on_off_heating_control():
    rooms_data = get_rooms_with_on_off_heating_control_data()
    radiators = get_radiators_to_update_for_on_off_heating_control(rooms_data)
    # Immediately turn off radiators that need to be turned off
    set_radiators_requested_state_to_off(radiators["ids_to_turn_off"])
    # Store the list of radiators to be turned on in the cache
    # to delegate their activation to the teleinfo listener
    # who has the better understanding of the available power
    set_radiators_to_turn_on_in_cache(radiators["to_turn_on"])
