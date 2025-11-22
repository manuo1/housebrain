import pytest
from actuators.models import Radiator
from heating.mappers import room_current_on_off_state_to_radiator_requested_state
from rooms.models import Room


@pytest.mark.parametrize(
    "room_state, expected_radiator_state",
    [
        (Room.CurrentHeatingState.ON, Radiator.RequestedState.ON),
        (Room.CurrentHeatingState.OFF, Radiator.RequestedState.OFF),
        (None, None),
        ("invalid_state", None),
    ],
)
def test_room_to_radiator_state_conversion(room_state, expected_radiator_state):
    result = room_current_on_off_state_to_radiator_requested_state(room_state)
    assert result == expected_radiator_state
