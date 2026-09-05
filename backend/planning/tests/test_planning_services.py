from datetime import time

import pytest

from planning.services import get_slot_data

TEMPERATURE_SLOTS = [
    {"start": "00:00", "end": "01:00", "type": "temp", "value": 1.0},
    {"start": "07:00", "end": "08:00", "type": "temp", "value": 2.0},
    {"start": "23:00", "end": "23:59", "type": "temp", "value": 3.0},
]
ONOFF_SLOTS = [
    {"start": "00:00", "end": "01:00", "type": "onoff", "value": "on"},
    {"start": "07:00", "end": "08:00", "type": "onoff", "value": "off"},
    {"start": "23:00", "end": "23:59", "type": "onoff", "value": "on"},
]


@pytest.mark.parametrize(
    "slots, searched_time, expected",
    [
        (TEMPERATURE_SLOTS, time(0, 0), ("temp", 1.0)),
        (TEMPERATURE_SLOTS, time(7, 2), ("temp", 2.0)),
        (TEMPERATURE_SLOTS, time(23, 59), ("temp", 3.0)),
        (ONOFF_SLOTS, time(0, 0), ("onoff", "on")),
        (ONOFF_SLOTS, time(7, 2), ("onoff", "off")),
        (ONOFF_SLOTS, time(23, 59), ("onoff", "on")),
        # No Slot for this time
        (TEMPERATURE_SLOTS, time(2, 0), (None, None)),
        (ONOFF_SLOTS, time(2, 0), (None, None)),
        # Missing field
        (
            [{"end": "01:00", "type": "onoff", "value": "on"}],
            time(2, 0),
            (None, None),
        ),
        (
            [{"start": "00:00", "type": "onoff", "value": "on"}],
            time(2, 0),
            (None, None),
        ),
        (
            [{"start": "00:00", "end": "01:00", "value": "on"}],
            time(2, 0),
            (None, None),
        ),
        (
            [{"start": "00:00", "end": "01:00", "type": "onoff"}],
            time(2, 0),
            (None, None),
        ),
        # searched_time or slots Not valid
        ({"start": "00:00", "end": "01:00", "type": "onoff"}, time(2, 0), (None, None)),
        (ONOFF_SLOTS, "02:00", (None, None)),
        # None
        (None, time(2, 0), (None, None)),
        (ONOFF_SLOTS, None, (None, None)),
        # Strange cases
        (
            [
                [],
                {"start": "00:00", "end": "01:00", "type": "onoff", "value": "on"},
            ],
            time(2, 0),
            (None, None),
        ),
        (
            [
                None,
                {"start": "00:00", "end": "01:00", "type": "onoff", "value": "on"},
            ],
            time(2, 0),
            (None, None),
        ),
    ],
)
def test_get_slot_data(slots, searched_time, expected):
    assert get_slot_data(slots, searched_time) == expected


def test_get_slot_data_returns_correct_slot():
    """Test that get_slot_data finds the correct slot for a given time"""
    slots = [
        {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
        {"start": "12:00", "end": "14:00", "type": "onoff", "value": "off"},
    ]

    slot_type, slot_value = get_slot_data(slots, time(8, 0))

    assert slot_type == "onoff"
    assert slot_value == "on"


def test_get_slot_data_returns_none_outside_slots():
    """Test that get_slot_data returns None when time is outside slots"""
    slots = [
        {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
    ]

    slot_type, slot_value = get_slot_data(slots, time(10, 0))

    assert slot_type is None
    assert slot_value is None


def test_get_slot_data_handles_invalid_slots():
    """Test that get_slot_data handles invalid slot format"""
    slots = [
        {"start": "invalid", "end": "09:00", "type": "onoff", "value": "on"},
    ]

    slot_type, slot_value = get_slot_data(slots, time(8, 0))

    assert slot_type is None
    assert slot_value is None


def test_get_slot_data_handles_empty_slots():
    """Test that get_slot_data handles empty slots list"""
    slot_type, slot_value = get_slot_data([], time(8, 0))

    assert slot_type is None
    assert slot_value is None


def test_get_slot_data_handles_none_inputs():
    """Test that get_slot_data handles None inputs"""
    slot_type, slot_value = get_slot_data(None, time(8, 0))

    assert slot_type is None
    assert slot_value is None

    slot_type, slot_value = get_slot_data([], None)

    assert slot_type is None
    assert slot_value is None


def test_get_slot_data_at_slot_boundaries():
    """Test that get_slot_data works correctly at slot boundaries"""
    slots = [
        {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
    ]

    # Test at start
    slot_type, slot_value = get_slot_data(slots, time(7, 0))
    assert slot_type == "onoff"
    assert slot_value == "on"

    # Test at end
    slot_type, slot_value = get_slot_data(slots, time(9, 0))
    assert slot_type == "onoff"
    assert slot_value == "on"

    # Test just before start
    slot_type, slot_value = get_slot_data(slots, time(6, 59))
    assert slot_type is None
    assert slot_value is None

    # Test just after end
    slot_type, slot_value = get_slot_data(slots, time(9, 1))
    assert slot_type is None
    assert slot_value is None
