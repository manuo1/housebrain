import pytest
from core.utils.energy_utils import wh_to_watt


@pytest.mark.parametrize(
    "wh, duration_minutes, expected",
    [
        (60, 60, 60),  # 60 Wh over 60 minutes = 60 W
        (30, 30, 60),  # 30 Wh over 30 minutes = 60 W
        (120, 30, 240),  # 120 Wh over 30 minutes = 240 W
        (0, 15, 0),  # 0 Wh = 0 W regardless of duration
        (None, 60, None),  # Invalid input: None as energy
        ("abc", 60, None),  # Invalid input: string instead of number
        (100, 0, None),  # Invalid input: division by zero duration
        (100, None, None),  # Invalid input: None as duration
    ],
)
def test_wh_to_watt(wh, duration_minutes, expected):
    assert wh_to_watt(wh, duration_minutes) == expected
