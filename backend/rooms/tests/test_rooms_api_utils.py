import pytest

from actuators.models import Radiator
from rooms.api.utils import (
    calculate_radiator_state,
    calculate_temperature_trend,
    get_mac_short,
)
from rooms.api.constants import (
    ApiRadiatorState,
)


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
    "current, previous, threshold, expected",
    [
        # Cas de hausse
        (21.5, 21.3, 0.1, "up"),
        (22.0, 21.5, 0.1, "up"),
        # Cas de baisse
        (20.0, 20.5, 0.1, "down"),
        (18.9, 19.1, 0.1, "down"),
        # Cas stable
        (20.0, 20.05, 0.1, "same"),
        (19.95, 20.0, 0.1, "same"),
        (20.0, 20.0, 0.1, "same"),
        # Cas limites avec seuil personnalisé
        (20.3, 20.0, 0.5, "same"),  # diff = 0.3 < 0.5
        (20.6, 20.0, 0.5, "up"),  # diff = 0.6 > 0.5
        (19.4, 20.0, 0.5, "down"),  # diff = -0.6 < -0.5
        # Cas invalides
        (None, 20.0, 0.1, None),
        (20.0, None, 0.1, None),
        (None, None, 0.1, None),
        # Mauvais types
        ("20.0", 19.0, 0.1, None),
        (20.0, "19.0", 0.1, None),
        ([], 20.0, 0.1, None),
        ({}, 20.0, 0.1, None),
    ],
)
def test_calculate_temperature_trend(current, previous, threshold, expected):
    assert calculate_temperature_trend(current, previous, threshold) == expected


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
