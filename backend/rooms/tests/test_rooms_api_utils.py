import pytest
from actuators.models import Radiator
from rooms.api.constants import ApiRadiatorState
from rooms.api.utils import calculate_radiator_state, get_mac_short


@pytest.mark.parametrize(
    "mac, expected",
    [
        ("A4:C1:38:46:C0:F4", "46:C0:F4"),
        (None, None),  # Valeur None
        ("", ""),  # Vide
        ("C1:38", "C1:38"),  # Trop court → renvoie la chaîne entière
        (123456, None),  # Mauvais type
    ],
)
def test_get_mac_short(mac, expected):
    assert get_mac_short(mac) == expected


def test_get_mac_short_handles_invalid_input():
    assert get_mac_short(None) is None
    assert get_mac_short(1234) is None
    assert get_mac_short(["AA:BB:CC"]) is None
    assert get_mac_short({"mac": "AA:BB:CC"}) is None


@pytest.mark.parametrize(
    "requested, actual, expected",
    [
        # === Normal states ===
        (Radiator.RequestedState.ON, Radiator.ActualState.ON, ApiRadiatorState.ON),
        (
            Radiator.RequestedState.ON,
            Radiator.ActualState.OFF,
            ApiRadiatorState.TURNING_ON,
        ),
        (Radiator.RequestedState.OFF, Radiator.ActualState.OFF, ApiRadiatorState.OFF),
        (
            Radiator.RequestedState.OFF,
            Radiator.ActualState.ON,
            ApiRadiatorState.SHUTTING_DOWN,
        ),
        # === Load shedding ===
        (
            Radiator.RequestedState.LOAD_SHED,
            Radiator.ActualState.ON,
            ApiRadiatorState.SHUTTING_DOWN,
        ),
        (
            Radiator.RequestedState.LOAD_SHED,
            Radiator.ActualState.OFF,
            ApiRadiatorState.LOAD_SHED,
        ),
        # === Hardware undefined ===
        (
            Radiator.RequestedState.ON,
            Radiator.ActualState.UNDEFINED,
            ApiRadiatorState.UNDEFINED,
        ),
        (
            Radiator.RequestedState.OFF,
            Radiator.ActualState.UNDEFINED,
            ApiRadiatorState.UNDEFINED,
        ),
        (
            Radiator.RequestedState.LOAD_SHED,
            Radiator.ActualState.UNDEFINED,
            ApiRadiatorState.UNDEFINED,
        ),
        # === Invalid / missing ===
        (None, Radiator.ActualState.ON, None),
        (Radiator.RequestedState.ON, None, None),
        (None, None, None),
    ],
)
def test_calculate_radiator_state(requested, actual, expected):
    """Ensure all possible radiator states are mapped correctly."""
    result = calculate_radiator_state(requested, actual)
    assert result == expected
