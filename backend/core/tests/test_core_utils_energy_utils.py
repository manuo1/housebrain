import pytest

from core.utils.energy_utils import split_by_available_power, wh_to_watt


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


ITEM_1 = {"id": 1, "power": 1000}
ITEM_2 = {"id": 2, "power": 1000}
ITEM_3 = {"id": 3, "power": 1000}


def test_split_by_available_power():
    can_turn_on, cannot_turn_on = split_by_available_power(
        [ITEM_1, ITEM_2, ITEM_3], remaining_power=2000
    )
    # remaining_power = 2000
    # ITEM_1 power + ITEM_2 power = 2000
    # Not enough power for ITEM_3
    assert can_turn_on == [ITEM_1, ITEM_2]
    assert cannot_turn_on == [ITEM_3]


@pytest.mark.parametrize("remaining_power", [None, 0, -100])
def test_split_by_available_power_nothing_safe_to_turn_on(remaining_power):
    can_turn_on, cannot_turn_on = split_by_available_power(
        [ITEM_1, ITEM_2], remaining_power=remaining_power
    )

    assert can_turn_on == []
    assert cannot_turn_on == [ITEM_1, ITEM_2]


def test_split_by_available_power_empty_items():
    can_turn_on, cannot_turn_on = split_by_available_power([], remaining_power=1000)

    assert can_turn_on == []
    assert cannot_turn_on == []
