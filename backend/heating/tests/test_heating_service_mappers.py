import pytest
from actuators.models import Radiator
from heating.mappers import radiator_state_matches_room_state
from rooms.models import Room


@pytest.mark.parametrize(
    "room_state, radiator_state, expected_match",
    [
        (Room.RequestedHeatingState.ON, Radiator.RequestedState.ON, True),
        (Room.RequestedHeatingState.ON, Radiator.RequestedState.OFF, False),
        (Room.RequestedHeatingState.ON, Radiator.RequestedState.LOAD_SHED, False),
        (Room.RequestedHeatingState.ON, None, False),
        #
        (Room.RequestedHeatingState.OFF, Radiator.RequestedState.ON, False),
        (Room.RequestedHeatingState.OFF, Radiator.RequestedState.OFF, True),
        (Room.RequestedHeatingState.OFF, Radiator.RequestedState.LOAD_SHED, True),
        (Room.RequestedHeatingState.OFF, None, False),
        #
        (Room.RequestedHeatingState.UNKNOWN, Radiator.RequestedState.ON, False),
        (Room.RequestedHeatingState.UNKNOWN, Radiator.RequestedState.OFF, False),
        (Room.RequestedHeatingState.UNKNOWN, Radiator.RequestedState.LOAD_SHED, False),
        (Room.RequestedHeatingState.UNKNOWN, None, False),
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
