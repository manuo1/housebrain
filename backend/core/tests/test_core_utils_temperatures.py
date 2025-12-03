import pytest
from core.utils.temperatures import validate_temperature_value


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
