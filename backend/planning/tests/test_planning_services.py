from datetime import date, time

import pytest

from planning.services import generate_duplication_dates, get_slot_data

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


# ------------------------------------------------------------------------------
# Tests for generate_duplication_dates
# ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "start_date, weekdays, end_date, expected",
    [
        # Basic case: single weekday, starts after start_date
        (
            date(2025, 12, 8),  # Monday
            [2],  # Wednesday
            date(2025, 12, 31),
            [
                date(2025, 12, 10),  # First Wednesday after start
                date(2025, 12, 17),
                date(2025, 12, 24),
                date(2025, 12, 31),
            ],
        ),
        # start_date falls ON a requested weekday - should be included
        (
            date(2025, 12, 10),  # Wednesday
            [2],  # Wednesday
            date(2025, 12, 31),
            [
                date(2025, 12, 10),  # start_date itself (it's a Wednesday)
                date(2025, 12, 17),
                date(2025, 12, 24),
                date(2025, 12, 31),
            ],
        ),
        # Requested weekday is earlier in the week than start_date
        (
            date(2025, 12, 11),  # Thursday
            [1],  # Tuesday (earlier in week)
            date(2025, 12, 30),
            [
                date(2025, 12, 16),  # Next Tuesday
                date(2025, 12, 23),
                date(2025, 12, 30),
            ],
        ),
        # Requested weekday is later in the same week as start_date
        (
            date(2025, 12, 8),  # Monday
            [5],  # Saturday (later in same week)
            date(2025, 12, 27),
            [
                date(2025, 12, 13),  # This Saturday
                date(2025, 12, 20),
                date(2025, 12, 27),
            ],
        ),
        # Multiple weekdays
        (
            date(2025, 12, 8),  # Monday
            [1, 3],  # Tuesday, Thursday
            date(2025, 12, 22),
            [
                date(2025, 12, 9),  # Tuesday
                date(2025, 12, 11),  # Thursday
                date(2025, 12, 16),  # Tuesday
                date(2025, 12, 18),  # Thursday
            ],
        ),
        # Multiple weekdays with start_date matching one of them
        (
            date(2025, 12, 9),  # Tuesday
            [1, 4],  # Tuesday, Friday
            date(2025, 12, 22),
            [
                date(2025, 12, 9),  # Tuesday (start_date)
                date(2025, 12, 12),  # Friday
                date(2025, 12, 16),  # Tuesday
                date(2025, 12, 19),  # Friday
            ],
        ),
        # Unsorted weekdays input - should produce sorted output
        (
            date(2025, 12, 8),  # Monday
            [5, 2, 6],  # Saturday, Wednesday, Sunday (unsorted)
            date(2025, 12, 21),
            [
                date(2025, 12, 10),  # Wednesday
                date(2025, 12, 13),  # Saturday
                date(2025, 12, 14),  # Sunday
                date(2025, 12, 17),  # Wednesday
                date(2025, 12, 20),  # Saturday
                date(2025, 12, 21),  # Sunday
            ],
        ),
        # Duplicate weekdays in input - should be deduplicated
        (
            date(2025, 12, 8),  # Monday
            [1, 1, 3, 1, 3],  # Duplicates: Tuesday and Thursday
            date(2025, 12, 18),
            [
                date(2025, 12, 9),  # Tuesday
                date(2025, 12, 11),  # Thursday
                date(2025, 12, 16),  # Tuesday
                date(2025, 12, 18),  # Thursday
            ],
        ),
        # All weekdays
        (
            date(2025, 12, 9),  # Tuesday
            [0, 1, 2, 3, 4, 5, 6],
            date(2025, 12, 16),
            [
                date(2025, 12, 9),  # Tuesday (start_date)
                date(2025, 12, 10),  # Wednesday
                date(2025, 12, 11),  # Thursday
                date(2025, 12, 12),  # Friday
                date(2025, 12, 13),  # Saturday
                date(2025, 12, 14),  # Sunday
                date(2025, 12, 15),  # Monday
                date(2025, 12, 16),  # Tuesday
            ],
        ),
        # Empty weekdays - should return empty list
        (
            date(2025, 12, 8),
            [],
            date(2025, 12, 31),
            [],
        ),
        # Very short range - no dates fit
        (
            date(2025, 12, 8),  # Monday
            [5],  # Saturday
            date(2025, 12, 12),  # Friday (before Saturday)
            [],
        ),
        # Very short range - exactly one date fits
        (
            date(2025, 12, 8),  # Monday
            [3],  # Thursday
            date(2025, 12, 11),  # Thursday (exact match)
            [
                date(2025, 12, 11),  # Thursday
            ],
        ),
        # end_date is exactly on a requested weekday
        (
            date(2025, 12, 8),  # Monday
            [2],  # Wednesday
            date(2025, 12, 17),  # Wednesday
            [
                date(2025, 12, 10),  # Wednesday
                date(2025, 12, 17),  # Wednesday (end_date, included)
            ],
        ),
        # start_date and end_date both on requested weekday
        (
            date(2025, 12, 10),  # Wednesday
            [2],  # Wednesday
            date(2025, 12, 24),  # Wednesday
            [
                date(2025, 12, 10),  # Wednesday (start_date)
                date(2025, 12, 17),  # Wednesday
                date(2025, 12, 24),  # Wednesday (end_date)
            ],
        ),
        # Long range with single weekday
        (
            date(2025, 1, 1),  # Wednesday
            [0],  # Monday
            date(2025, 1, 31),
            [
                date(2025, 1, 6),
                date(2025, 1, 13),
                date(2025, 1, 20),
                date(2025, 1, 27),
            ],
        ),
    ],
)
def test_generate_duplication_dates(start_date, weekdays, end_date, expected):
    """Test generate_duplication_dates with various scenarios"""
    result = generate_duplication_dates(start_date, weekdays, end_date)

    assert result == expected
    # Verify result is always sorted
    assert result == sorted(result)
    # Verify no duplicates
    assert len(result) == len(set(result))
    # Verify all dates are in valid range
    assert all(start_date <= d <= end_date for d in result)
    # Verify all dates have correct weekdays
    assert all(d.weekday() in weekdays for d in result)


@pytest.mark.parametrize("weekday", [0, 1, 2, 3, 4, 5, 6])
def test_generate_duplication_dates_individual_weekdays(weekday):
    """Test each weekday individually to ensure correct filtering"""
    start_date = date(2025, 12, 1)
    end_date = date(2025, 12, 31)

    result = generate_duplication_dates(start_date, [weekday], end_date)

    # All returned dates must be the requested weekday
    assert all(d.weekday() == weekday for d in result)
    # All dates must be in range
    assert all(start_date <= d <= end_date for d in result)
    # Result must be sorted
    assert result == sorted(result)
    # Consecutive dates must be exactly 7 days apart (weekly recurrence)
    for i in range(len(result) - 1):
        assert (result[i + 1] - result[i]).days == 7


def test_generate_duplication_dates_three_month_range():
    """Test with a longer date range to verify consistency over multiple months"""
    start_date = date(2025, 1, 1)  # Wednesday
    end_date = date(2025, 3, 31)
    weekdays = [0, 4]  # Monday and Friday

    result = generate_duplication_dates(start_date, weekdays, end_date)

    # Verify all dates have correct weekdays
    assert all(d.weekday() in [0, 4] for d in result)
    # Verify range
    assert all(start_date <= d <= end_date for d in result)
    # Verify sorted
    assert result == sorted(result)
    # Should have roughly 13 Mondays + 13 Fridays = ~26 dates
    assert 20 <= len(result) <= 30


def test_generate_duplication_dates_boundary_conditions():
    """Test edge cases with start_date and end_date"""
    # Case 1: start_date = end_date, both on requested weekday
    start = date(2025, 12, 10)  # Wednesday
    result = generate_duplication_dates(start, [2], start)
    assert result == [start]

    # Case 2: start_date = end_date, NOT on requested weekday
    start = date(2025, 12, 10)  # Wednesday
    result = generate_duplication_dates(start, [0], start)  # Monday
    assert result == []

    # Case 3: Range of exactly 7 days with one matching weekday
    start = date(2025, 12, 8)  # Monday
    end = date(2025, 12, 15)  # Next Monday
    result = generate_duplication_dates(start, [0], end)
    assert result == [date(2025, 12, 8), date(2025, 12, 15)]


def test_generate_duplication_dates_preserves_order_with_random_input():
    """Verify output is sorted regardless of input weekday order"""
    start_date = date(2025, 12, 1)
    end_date = date(2025, 12, 31)

    # Test with different orderings of the same weekdays
    weekdays_orders = [
        [6, 0, 3, 1],
        [0, 1, 3, 6],
        [3, 6, 1, 0],
    ]

    results = [
        generate_duplication_dates(start_date, order, end_date)
        for order in weekdays_orders
    ]

    # All should produce the same sorted result
    assert results[0] == results[1] == results[2]
    assert results[0] == sorted(results[0])
