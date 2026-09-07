import logging

from django.utils import timezone

from actuators.mutators.radiators import (
    apply_load_shedding_to_radiators,
    set_radiators_requested_state_to_off,
    set_radiators_requested_state_to_on,
)
from actuators.services.radiator_synchronization import RadiatorSyncService
from core.utils.temperatures import validate_temperature_value
from heating.mappers import (
    heating_pattern_slot_value_to_room_requested_heating_state,
    radiator_state_matches_room_state,
)
from heating.selectors.heating import get_rooms_heating_plans_data
from heating.services.thermostat import get_requested_heating_state_based_on_temperature
from heating.utils.cache_heating import (
    get_radiators_to_turn_on_in_cache,
    set_radiators_to_turn_on_in_cache,
)
from planning.models import SchedulePattern
from planning.services import get_slot_data
from rooms.models import Room
from rooms.mutators.rooms import update_room_heating_fields
from rooms.selectors.heating import get_rooms_heating_state_data

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


def split_radiators_by_available_power(radiators: list, remaining_power: int):
    can_turn_on = []
    cannot_turn_on = []

    for radiator in radiators:
        if remaining_power >= radiator["power"]:
            can_turn_on.append(radiator)
            remaining_power -= radiator["power"]
        else:
            cannot_turn_on.append(radiator)

    return can_turn_on, cannot_turn_on


def turn_on_radiators_according_to_the_available_power(remaining_power: int | None):
    radiators = get_radiators_to_turn_on_in_cache()
    if not radiators:
        return
    sorted_radiators = sorted(radiators, key=lambda x: (x["importance"], -x["power"]))
    can_turn_on, cannot_turn_on = split_radiators_by_available_power(
        sorted_radiators, remaining_power
    )

    # Keep the radiators that couldn't be turned on in the cache to try again.
    set_radiators_to_turn_on_in_cache(cannot_turn_on)
    # Turn on the radiators that can.
    set_radiators_requested_state_to_on([radiator["id"] for radiator in can_turn_on])
    # Indicates that the others are experiencing load shedding.
    apply_load_shedding_to_radiators([radiator["id"] for radiator in cannot_turn_on])


def resolve_radiators_to_update() -> dict:
    rooms_data = get_rooms_heating_state_data()
    return get_radiators_to_update(rooms_data)


def turn_off_radiators_and_apply_to_hardware(radiators_to_update: dict) -> None:
    """
    Writes requested_state = OFF for the given radiators, then immediately
    applies the change to hardware. Turning off is never a power problem,
    so no need to wait for the listener.

    Note: RadiatorSyncService works on the whole radiator fleet at once
    (single batched I2C read/write) — it can't be scoped to just these
    radiators, so this also re-applies every other radiator's current
    requested_state, unchanged.
    """
    set_radiators_requested_state_to_off(radiators_to_update["ids_to_turn_off"])
    RadiatorSyncService.synchronize_database_and_hardware()


def queue_radiators_to_turn_on(radiators_to_update: dict) -> None:
    """
    Queues the given radiators into the cache. Does NOT change their
    requested_state or touch hardware — the teleinfo listener, the only
    one that knows the available power in real time, decides from there.
    """
    set_radiators_to_turn_on_in_cache(radiators_to_update["to_turn_on"])


def room_plan_keys_are_valides(room_plan: dict) -> bool:
    if not isinstance(room_plan, dict):
        return False
    required_fields = {
        "room_id",
        "heating_pattern__slots",
        "room__temperature_sensor__mac_address",
        "room__heating_control_mode",
        "room__temperature_setpoint",
        "room__requested_heating_state",
    }
    return required_fields.issubset(room_plan.keys())


def synchronize_room_requested_heating_states_with_room_heating_day_plan():
    now = timezone.localtime(timezone.now())
    rooms_heating_plans = get_rooms_heating_plans_data(now.date())
    # if a room don't have day plan for this day
    # nothing will change on this room
    for room_plan in rooms_heating_plans:
        if not room_plan_keys_are_valides(room_plan):
            continue
        heating_control_mode = Room.HeatingControlMode.ONOFF
        temperature_setpoint = None
        requested_heating_state = Room.RequestedHeatingState.OFF
        setpoint_type, setpoint_value = get_slot_data(
            room_plan["heating_pattern__slots"], now.time()
        )

        match setpoint_type:
            case SchedulePattern.SlotType.TEMPERATURE:
                heating_control_mode = Room.HeatingControlMode.THERMOSTAT
                temperature_setpoint = validate_temperature_value(setpoint_value)
                # Falls back to the room's current state (not OFF) when the
                # thermostat can't decide (e.g. missing/faulty sensor)
                requested_heating_state = (
                    get_requested_heating_state_based_on_temperature(
                        temperature_setpoint,
                        room_plan["room__temperature_sensor__mac_address"],
                    )
                ) or room_plan["room__requested_heating_state"]

            case SchedulePattern.SlotType.ONOFF:
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
