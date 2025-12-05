from unittest.mock import patch

import pytest
from heating.constants import HYSTERESIS
from heating.services.thermostat import get_requested_heating_state_based_on_temperature
from rooms.models import Room

T_SETPOINT = 20
T_WELL_ABOVE = T_SETPOINT + HYSTERESIS
T_WELL_BELOW = T_SETPOINT - HYSTERESIS
T_JUST_ABOVE = T_SETPOINT + HYSTERESIS / 2
T_JUST_BELOW = T_SETPOINT - HYSTERESIS / 2
T_DELTA = 0.1  # calculate_temperature_trend() threshold

TURN_OFF = Room.RequestedHeatingState.OFF
TURN_ON = Room.RequestedHeatingState.ON


@pytest.mark.parametrize(
    "current_temp, previous_temp, expected_state",
    [
        # No temperature
        (None, None, None),
        # No Trend, current but no previous
        (T_WELL_ABOVE, None, TURN_OFF),
        (T_JUST_ABOVE, None, None),
        (T_SETPOINT, None, None),
        (T_JUST_BELOW, None, None),
        (T_WELL_BELOW, None, TURN_ON),
        # No Trend, current None -> fallback on previous
        (None, T_WELL_ABOVE, TURN_OFF),
        (None, T_JUST_ABOVE, None),
        (None, T_SETPOINT, None),
        (None, T_JUST_BELOW, None),
        (None, T_WELL_BELOW, TURN_ON),
        # Trend DOWN
        (T_WELL_ABOVE, T_WELL_ABOVE + T_DELTA, TURN_OFF),
        (T_JUST_ABOVE, T_JUST_ABOVE + T_DELTA, TURN_ON),
        (T_SETPOINT, T_SETPOINT + T_DELTA, TURN_ON),
        (T_JUST_BELOW, T_JUST_BELOW + T_DELTA, TURN_ON),
        (T_WELL_BELOW, T_WELL_BELOW + T_DELTA, TURN_ON),
        # Trend UP
        (T_WELL_ABOVE, T_WELL_ABOVE - T_DELTA, TURN_OFF),
        (T_JUST_ABOVE, T_JUST_ABOVE - T_DELTA, TURN_OFF),
        (T_SETPOINT, T_SETPOINT - T_DELTA, TURN_OFF),
        (T_JUST_BELOW, T_JUST_BELOW - T_DELTA, TURN_OFF),
        (T_WELL_BELOW, T_WELL_BELOW - T_DELTA, TURN_ON),
        # Trend SAME
        (T_WELL_ABOVE, T_WELL_ABOVE, TURN_OFF),
        (T_JUST_ABOVE, T_JUST_ABOVE, TURN_OFF),
        (T_SETPOINT, T_SETPOINT, TURN_ON),
        (T_JUST_BELOW, T_JUST_BELOW, TURN_ON),
        (T_WELL_BELOW, T_WELL_BELOW, TURN_ON),
    ],
)
def test_get_requested_state(current_temp, previous_temp, expected_state):
    with (
        patch(
            "heating.services.thermostat.get_sensor_temperatures",
            return_value=(current_temp, previous_temp),
        ),
    ):
        assert (
            get_requested_heating_state_based_on_temperature(T_SETPOINT, "mac")
            == expected_state
        )


@pytest.mark.parametrize(
    "temperature_setpoint, mac_address",
    [
        (None, "mac"),
        ("a", "mac"),
        ([], "mac"),
        (20.1, None),
        (20.1, 1),
        (20.1, []),
    ],
)
def test_get_requested_state_invalid_param(temperature_setpoint, mac_address):
    assert (
        get_requested_heating_state_based_on_temperature(
            temperature_setpoint, mac_address
        )
        == None
    )
