import pytest

from equipment.models import WaterHeater
from water_heater.mappers import (
    schedule_pattern_slot_value_to_water_heater_requested_state,
    water_heater_state_matches_plan_state,
)


@pytest.mark.parametrize(
    "plan_state, water_heater_state, expected",
    [
        (WaterHeater.RequestedState.ON, WaterHeater.RequestedState.ON, True),
        (WaterHeater.RequestedState.ON, WaterHeater.RequestedState.OFF, False),
        (WaterHeater.RequestedState.ON, WaterHeater.RequestedState.LOAD_SHED, False),
        (WaterHeater.RequestedState.OFF, WaterHeater.RequestedState.OFF, True),
        (WaterHeater.RequestedState.OFF, WaterHeater.RequestedState.LOAD_SHED, True),
        (WaterHeater.RequestedState.OFF, WaterHeater.RequestedState.ON, False),
        (None, None, True),
        (None, WaterHeater.RequestedState.ON, False),
    ],
)
def test_water_heater_state_matches_plan_state(plan_state, water_heater_state, expected):
    assert water_heater_state_matches_plan_state(plan_state, water_heater_state) == expected


@pytest.mark.parametrize(
    "slot_value, expected",
    [
        ("on", WaterHeater.RequestedState.ON),
        ("off", WaterHeater.RequestedState.OFF),
        ("maybe", None),
        (None, None),
        (123, None),
    ],
)
def test_schedule_pattern_slot_value_to_water_heater_requested_state(
    slot_value, expected
):
    assert (
        schedule_pattern_slot_value_to_water_heater_requested_state(slot_value)
        == expected
    )
