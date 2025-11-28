import pytest
from actuators.models import Radiator
from heating.mappers import (
    heating_pattern_slot_value_to_room_requested_heating_state,
    radiator_state_matches_room_state,
)
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


@pytest.mark.parametrize(
    "heating_pattern_slot_value, room_requested_heating_state",
    [
        ("on", Room.RequestedHeatingState.ON),
        ("off", Room.RequestedHeatingState.OFF),
        ("not_on_or_off", Room.RequestedHeatingState.UNKNOWN),
        (None, Room.RequestedHeatingState.UNKNOWN),
        ([], Room.RequestedHeatingState.UNKNOWN),
        ({}, Room.RequestedHeatingState.UNKNOWN),
    ],
)
def test_heating_pattern_slot_value_to_room_requested_heating_state(
    heating_pattern_slot_value, room_requested_heating_state
):
    assert (
        heating_pattern_slot_value_to_room_requested_heating_state(
            heating_pattern_slot_value
        )
        == room_requested_heating_state
    )
