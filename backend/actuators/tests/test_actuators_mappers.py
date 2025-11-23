import pytest
from actuators.mappers import RadiatorStateMapper
from actuators.models import Radiator
from actuators.constants import MCP23017PinState


@pytest.mark.parametrize(
    "requested_state, expected_pin",
    [
        (Radiator.RequestedState.ON, False),
        (Radiator.RequestedState.OFF, True),
        (Radiator.RequestedState.LOAD_SHED, True),
    ],
)
def test_requested_state_to_pin_state(requested_state, expected_pin):
    result = RadiatorStateMapper.radiator_requested_state_to_pin_state(requested_state)
    assert result == expected_pin


@pytest.mark.parametrize(
    "pin_state, expected_actual_state",
    [
        (MCP23017PinState.ON, Radiator.ActualState.OFF),
        (MCP23017PinState.OFF, Radiator.ActualState.ON),
        (MCP23017PinState.UNDEFINED, Radiator.ActualState.UNDEFINED),
    ],
)
def test_pin_state_to_radiator_state(pin_state, expected_actual_state):
    result = RadiatorStateMapper.pin_state_to_radiator_state(pin_state)
    assert result == expected_actual_state
