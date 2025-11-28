from actuators.models import Radiator
from rooms.models import Room


def radiator_state_matches_room_state(
    room_current_heatingState: Room.RequestedHeatingState,
    radiator_requested_state: Radiator.RequestedState,
) -> bool:
    match room_current_heatingState:
        case Room.RequestedHeatingState.UNKNOWN:
            return False
        case Room.RequestedHeatingState.ON:
            return radiator_requested_state == Radiator.RequestedState.ON
        case Room.RequestedHeatingState.OFF:
            return radiator_requested_state in (
                Radiator.RequestedState.OFF,
                Radiator.RequestedState.LOAD_SHED,
            )
        case None:
            return radiator_requested_state is None
        case _:
            return False


def heating_pattern_slot_value_to_room_requested_heating_state(
    slot_value: str,
) -> Room.RequestedHeatingState:
    if not isinstance(slot_value, str):
        return Room.RequestedHeatingState.UNKNOWN
    mapping = {
        "on": Room.RequestedHeatingState.ON,
        "off": Room.RequestedHeatingState.OFF,
    }
    return mapping.get(slot_value, Room.RequestedHeatingState.UNKNOWN)
