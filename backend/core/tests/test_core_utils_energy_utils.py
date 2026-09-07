import pytest

from core.utils.energy_utils import (
    select_items_for_load_shedding,
    split_by_available_power,
    wh_to_watt,
)


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


ITEMS_ON = [
    {"id": 2, "power": 750, "importance": 3},
    {"id": 11, "power": 1250, "importance": 3},
    {"id": 4, "power": 750, "importance": 2},
    {"id": 5, "power": 1000, "importance": 2},
    {"id": 10, "power": 1500, "importance": 2},
    {"id": 13, "power": 1500, "importance": 2},
    {"id": 3, "power": 1500, "importance": 1},
    {"id": 8, "power": 1500, "importance": 1},
]


@pytest.mark.parametrize(
    "remaining_power, items_on, expected",
    [
        # -500w restant (soit 1500w avant marge) + 750w de id=2 = 250w, encore déficitaire de 750-500=250 recouvert par id=11 seul
        (1500 - 2000, ITEMS_ON, [2]),
        # -2000w restant (soit 0w avant marge) + 750w de id=2 + 1250w de id=11 = 2000w pile
        (0 - 2000, ITEMS_ON, [2, 11]),
        # si la puissance consommée est supérieur à la puissance autorisée
        (-1500 - 2000, ITEMS_ON, [2, 11, 4, 5]),
        # Plus d'accès à la teleinfo -> éteint tout sauf importance 0 et 1
        (None, ITEMS_ON, [2, 11, 4, 5, 10, 13]),
    ],
)
def test_select_items_for_load_shedding(remaining_power, items_on, expected):
    assert select_items_for_load_shedding(remaining_power, items_on) == expected
