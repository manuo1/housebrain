from actuators.models import Radiator
from rooms.models import Room


def radiator_state_matches_room_state(
    room_current_heatingState: Room.CurrentHeatingState,
    radiator_requested_state: Radiator.RequestedState,
) -> bool:
    match room_current_heatingState:
        case Room.CurrentHeatingState.UNKNOWN:
            return False
        case Room.CurrentHeatingState.ON:
            return radiator_requested_state == Radiator.RequestedState.ON
        case Room.CurrentHeatingState.OFF:
            return radiator_requested_state in (
                Radiator.RequestedState.OFF,
                Radiator.RequestedState.LOAD_SHED,
            )
        case None:
            return radiator_requested_state is None
        case _:
            return False
