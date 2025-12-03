import logging
from datetime import time

from actuators.constants import POWER_SAFETY_MARGIN
from actuators.mutators.radiators import (
    apply_load_shedding_to_radiators,
    set_radiators_requested_state_to_off,
    set_radiators_requested_state_to_on,
)
from django.utils import timezone
from heating.mappers import (
    heating_pattern_slot_value_to_room_requested_heating_state,
    radiator_state_matches_room_state,
)
from heating.models import HeatingPattern
from heating.selectors.heating import get_rooms_heating_plans_data
from heating.utils.cache_heating import (
    get_radiators_to_turn_on_in_cache,
    set_radiators_to_turn_on_in_cache,
)
from rooms.models import Room
from rooms.mutators.rooms import update_room_heating_fields
from rooms.selectors.heating import get_rooms_heating_state_data
from teleinfo.utils.cache_teleinfo_data import get_instant_available_power

logger = logging.getLogger("django")


def get_radiators_to_update(rooms_data: list[dict]) -> list:
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
    remaining_power = get_instant_available_power() - POWER_SAFETY_MARGIN

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


def synchronize_room_heating_states_with_radiators():
    rooms_data = get_rooms_heating_state_data()
    radiators = get_radiators_to_update(rooms_data)
    # Immediately turn off radiators that need to be turned off
    set_radiators_requested_state_to_off(radiators["ids_to_turn_off"])
    # Store the list of radiators to be turned on in the cache
    # to delegate their activation to the teleinfo listener
    # who has the better understanding of the available power
    set_radiators_to_turn_on_in_cache(radiators["to_turn_on"])


def get_slot_data(slots: list, searched_time: time) -> tuple:
    if not isinstance(slots, list) or not isinstance(searched_time, time):
        return None, None

    for slot in slots:
        try:
            start_h, start_m = map(int, slot["start"].split(":"))
            end_h, end_m = map(int, slot["end"].split(":"))
            start_t = time(start_h, start_m)
            end_t = time(end_h, end_m)
        except (ValueError, KeyError, TypeError):
            continue

        if start_t <= searched_time <= end_t:
            try:
                return slot["type"], slot["value"]
            except (ValueError, KeyError):
                continue

    return None, None


def validate_temperature_setpoint(setpoint_value: object) -> float | None:
    if isinstance(setpoint_value, bool):
        return
    try:
        return float(setpoint_value)
    except (ValueError, TypeError):
        return


def synchronize_room_requested_heating_states_with_room_heating_day_plan():
    now = timezone.localtime(timezone.now())
    rooms_heating_plans = get_rooms_heating_plans_data(now.date())
    # if a room don't have day plan for this day
    # nothing will change on this room
    for room_plan in rooms_heating_plans:
        heating_control_mode = Room.HeatingControlMode.ONOFF
        temperature_setpoint = None
        requested_heating_state = Room.RequestedHeatingState.OFF
        setpoint_type, setpoint_value = get_slot_data(
            room_plan["heating_pattern__slots"], now.time()
        )

        match setpoint_type:
            case HeatingPattern.SlotType.TEMPERATURE:
                heating_control_mode = Room.HeatingControlMode.THERMOSTAT
                temperature_setpoint = validate_temperature_setpoint(setpoint_value)
                # TODO implement thermostat control
                # get temp from cache with sensor mac_address
                # get requested_heating_state to keep temperature

            case HeatingPattern.SlotType.ONOFF:
                temperature_setpoint = None
                requested_heating_state = (
                    heating_pattern_slot_value_to_room_requested_heating_state(
                        setpoint_value
                    )
                )

        if any(
            {
                room_plan["room__heating_control_mode"] != heating_control_mode,
                room_plan["room__temperature_setpoint"] != temperature_setpoint,
                room_plan["room__requested_heating_state"] != requested_heating_state,
            }
        ):
            update_room_heating_fields(
                room_plan["room_id"],
                heating_control_mode,
                temperature_setpoint,
                requested_heating_state,
            )
