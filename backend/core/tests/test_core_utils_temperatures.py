import pytest
from core.utils.temperatures import (
    calculate_temperature_trend,
    validate_temperature_value,
)


@pytest.mark.parametrize(
    "setpoint, expected",
    [
        (1, 1.0),
        (1.1, 1.1),
        ("1", 1.0),
        ("1.1", 1.1),
        ("on", None),
        ("off", None),
        ([], None),
        ({}, None),
        (None, None),
        (False, None),
    ],
)
def test_validate_temperature_setpoint(setpoint, expected):
    assert validate_temperature_value(setpoint) == expected


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
