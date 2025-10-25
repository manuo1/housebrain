from actuators.models import Radiator
from rooms.models import Room


class RoomAndRadiatorStateMapper:
    """
    Maps between Room heating states and Radiator requested states.
    """

    @staticmethod
    def room_current_on_off_state_to_radiator_requested_state(
        room_current_on_off_state: Room.CurrentHeatingState,
    ) -> Radiator.RequestedState | None:
        """
        Convert a Room heating state into a Radiator requested state.
        """
        match room_current_on_off_state:
            case Room.CurrentHeatingState.ON:
                return Radiator.RequestedState.ON
            case Room.CurrentHeatingState.OFF:
                return Radiator.RequestedState.OFF
            case _:
                return None
