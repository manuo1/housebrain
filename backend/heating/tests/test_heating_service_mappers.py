import pytest
from actuators.models import Radiator
from heating.mappers import radiator_state_matches_room_state
from rooms.models import Room


@pytest.mark.parametrize(
    "room_state, radiator_state, expected_match",
    [
        (Room.CurrentHeatingState.ON, Radiator.RequestedState.ON, True),
        (Room.CurrentHeatingState.ON, Radiator.RequestedState.OFF, False),
        (Room.CurrentHeatingState.ON, Radiator.RequestedState.LOAD_SHED, False),
        (Room.CurrentHeatingState.ON, None, False),
        #
        (Room.CurrentHeatingState.OFF, Radiator.RequestedState.ON, False),
        (Room.CurrentHeatingState.OFF, Radiator.RequestedState.OFF, True),
        (Room.CurrentHeatingState.OFF, Radiator.RequestedState.LOAD_SHED, True),
        (Room.CurrentHeatingState.OFF, None, False),
        #
        (Room.CurrentHeatingState.UNKNOWN, Radiator.RequestedState.ON, False),
        (Room.CurrentHeatingState.UNKNOWN, Radiator.RequestedState.OFF, False),
        (Room.CurrentHeatingState.UNKNOWN, Radiator.RequestedState.LOAD_SHED, False),
        (Room.CurrentHeatingState.UNKNOWN, None, False),
        #
        (None, Radiator.RequestedState.ON, False),
        (None, Radiator.RequestedState.OFF, False),
        (None, Radiator.RequestedState.LOAD_SHED, False),
        (None, None, True),
    ],
)
def test_radiator_state_matches_room_state(room_state, radiator_state, expected_match):
    assert (
        radiator_state_matches_room_state(room_state, radiator_state) == expected_match
    )
