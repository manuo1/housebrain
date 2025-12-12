from datetime import date, timedelta
from unittest.mock import patch

import pytest
from heating.api.constants import DayStatus
from heating.api.services import (
    DuplicationTypes,
    add_day_status,
    error_in_duplication_dates,
    generate_duplication_dates,
    group_slots_hashes_by_date,
)

DEFAULT_DATE_1 = date(2025, 12, 9)

DEFAULT_DATE_2 = date(2025, 12, 10)

HASH_1 = "slots_hash_1"
HASH_2 = "slots_hash_2"
HASH_3 = "slots_hash_3"
SLOTS_HASHES = [
    (DEFAULT_DATE_1, HASH_1),
    (DEFAULT_DATE_1, HASH_2),
    (DEFAULT_DATE_2, HASH_3),
]


def test_group_slots_hashes_by_date_normal_case():
    result = group_slots_hashes_by_date(SLOTS_HASHES)
    assert result == {DEFAULT_DATE_1: {HASH_1, HASH_2}, DEFAULT_DATE_2: {HASH_3}}


@pytest.mark.parametrize(
    "slots_hashes, result",
    [
        ([], {}),
        (None, {}),
        (date(2025, 1, 1), {}),
        (False, {}),
        ([1, 2], {}),
        ({}, {}),
    ],
)
def test_group_slots_hashes_by_date_other_cases(slots_hashes, result):
    assert group_slots_hashes_by_date(slots_hashes) == result


def test_add_day_status_normal_case():
    heating_calendar = [
        # have heating plans
        {"date": date(2025, 12, 9), "status": DayStatus.EMPTY},
        # have heating plans
        {"date": date(2025, 12, 10), "status": DayStatus.EMPTY},
        # don't have heating plans
        {"date": date(2025, 12, 11), "status": DayStatus.EMPTY},
    ]
    slots_hashes = [
        ## -------------------------
        # day one week before 2025-12-9 same hashes
        (date(2025, 12, 9) - timedelta(weeks=1), HASH_1),
        (date(2025, 12, 9) - timedelta(weeks=1), HASH_2),
        # 2025-12-9 should be Normal because all hash are identical
        (date(2025, 12, 9), HASH_1),
        (date(2025, 12, 9), HASH_2),
        ## -------------------------
        # day one week before 2025-12-10
        (date(2025, 12, 10) - timedelta(weeks=1), HASH_2),
        # 2025-12-10 should be different because hash are different
        (date(2025, 12, 10), HASH_3),
        ## -------------------------
        # day one week before 2025-12-11
        (date(2025, 12, 11) - timedelta(weeks=1), HASH_1),
    ]

    with (
        patch("heating.api.services.get_slots_hashes", return_value=slots_hashes),
    ):
        add_day_status(heating_calendar)

        assert heating_calendar == [
            {"date": date(2025, 12, 9), "status": DayStatus.NORMAL},
            {"date": date(2025, 12, 10), "status": DayStatus.DIFFERENT},
            {"date": date(2025, 12, 11), "status": DayStatus.EMPTY},
        ]


@pytest.mark.parametrize(
    "raw_heating_calendar, slots_hashes, heating_calendar",
    [
        ([{"unknow": date(2025, 12, 9), "status": DayStatus.EMPTY}], [], []),
        ([{"date": 1, "status": DayStatus.EMPTY}], [], []),
        (
            [
                {"date": date(2025, 12, 11), "status": DayStatus.EMPTY},
                {"unknow": date(2025, 12, 11), "status": DayStatus.EMPTY},
            ],
            [],
            [],
        ),
        (None, [], []),
        ([], [], []),
    ],
)
def test_add_day_status_return_empty_list(
    raw_heating_calendar, slots_hashes, heating_calendar
):
    with (
        patch("heating.api.services.get_slots_hashes", return_value=slots_hashes),
    ):
        assert add_day_status(raw_heating_calendar) == heating_calendar


# Tests for error_in_duplication_dates


@pytest.mark.parametrize(
    "source_date, end_date, duplication_type, expected_error",
    [
        # source_date >= end_date
        (
            DEFAULT_DATE_1,
            DEFAULT_DATE_1,
            DuplicationTypes.WEEK,
            "source_date must be before repeat_until",
        ),
        (
            DEFAULT_DATE_1,
            DEFAULT_DATE_1 - timedelta(days=1),
            DuplicationTypes.WEEK,
            "source_date must be before repeat_until",
        ),
        (
            DEFAULT_DATE_1 + timedelta(days=10),
            DEFAULT_DATE_1,
            DuplicationTypes.WEEK,
            "source_date must be before repeat_until",
        ),
        # More than 366 days
        (
            DEFAULT_DATE_1,
            DEFAULT_DATE_1 + timedelta(days=367),
            DuplicationTypes.WEEK,
            "Maximum 365 days between source_date and repeat_until",
        ),
        (
            DEFAULT_DATE_1,
            DEFAULT_DATE_1 + timedelta(days=400),
            DuplicationTypes.WEEK,
            "Maximum 365 days between source_date and repeat_until",
        ),
        # WEEK duplication with less than 7 days
        (
            DEFAULT_DATE_1,
            DEFAULT_DATE_1 + timedelta(days=1),
            DuplicationTypes.WEEK,
            "There must be at least 7 days between source_date and repeat_until in the case of a duplication of weeks",
        ),
        (
            DEFAULT_DATE_1,
            DEFAULT_DATE_1 + timedelta(days=6),
            DuplicationTypes.WEEK,
            "There must be at least 7 days between source_date and repeat_until in the case of a duplication of weeks",
        ),
    ],
)
def test_error_in_duplication_dates_with_errors(
    source_date, end_date, duplication_type, expected_error
):
    """Test error_in_duplication_dates returns correct error messages"""
    result = error_in_duplication_dates(source_date, end_date, duplication_type)
    assert result == expected_error


@pytest.mark.parametrize(
    "source_date, end_date, duplication_type",
    [
        # Valid WEEK duplication
        (DEFAULT_DATE_1, DEFAULT_DATE_1 + timedelta(days=7), DuplicationTypes.WEEK),
        (DEFAULT_DATE_1, DEFAULT_DATE_1 + timedelta(days=14), DuplicationTypes.WEEK),
        (DEFAULT_DATE_1, DEFAULT_DATE_1 + timedelta(days=365), DuplicationTypes.WEEK),
        (DEFAULT_DATE_1, DEFAULT_DATE_1 + timedelta(days=366), DuplicationTypes.WEEK),
        # Valid non-WEEK duplication (less than 7 days is OK)
        (DEFAULT_DATE_1, DEFAULT_DATE_1 + timedelta(days=1), "DAILY"),
        (DEFAULT_DATE_1, DEFAULT_DATE_1 + timedelta(days=3), "DAILY"),
        (DEFAULT_DATE_1, DEFAULT_DATE_1 + timedelta(days=6), "OTHER"),
        # Exactly 365 days
        (DEFAULT_DATE_1, DEFAULT_DATE_1 + timedelta(days=365), "DAILY"),
    ],
)
def test_error_in_duplication_dates_no_errors(source_date, end_date, duplication_type):
    """Test error_in_duplication_dates returns None for valid inputs"""
    result = error_in_duplication_dates(source_date, end_date, duplication_type)
    assert result is None


# Tests for generate_duplication_dates


def test_generate_duplication_dates_single_weekday():
    """Test generating dates for a single weekday"""
    # Tuesday (1) starting from Monday 2025-12-08
    source_date = date(2025, 12, 8)  # Monday
    end_date = date(2025, 12, 31)
    weekdays = [1]  # Tuesday

    result = generate_duplication_dates(source_date, weekdays, end_date)

    expected = [
        date(2025, 12, 9),  # Tuesday
        date(2025, 12, 16),  # Tuesday
        date(2025, 12, 23),  # Tuesday
        date(2025, 12, 30),  # Tuesday
    ]
    assert result == expected


def test_generate_duplication_dates_multiple_weekdays():
    """Test generating dates for multiple weekdays"""
    source_date = date(2025, 12, 8)  # Monday
    end_date = date(2025, 12, 22)
    weekdays = [1, 3, 5]  # Tuesday, Thursday, Saturday

    result = generate_duplication_dates(source_date, weekdays, end_date)

    expected = [
        date(2025, 12, 9),  # Tuesday
        date(2025, 12, 11),  # Thursday
        date(2025, 12, 13),  # Saturday
        date(2025, 12, 16),  # Tuesday
        date(2025, 12, 18),  # Thursday
        date(2025, 12, 20),  # Saturday
    ]
    assert result == expected


def test_generate_duplication_dates_all_weekdays():
    """Test generating dates for all weekdays"""
    source_date = date(2025, 12, 8)  # Monday
    end_date = date(2025, 12, 15)
    weekdays = [0, 1, 2, 3, 4, 5, 6]  # All days

    result = generate_duplication_dates(source_date, weekdays, end_date)

    expected = [
        date(2025, 12, 9),  # Tuesday
        date(2025, 12, 10),  # Wednesday
        date(2025, 12, 11),  # Thursday
        date(2025, 12, 12),  # Friday
        date(2025, 12, 13),  # Saturday
        date(2025, 12, 14),  # Sunday
        date(2025, 12, 15),  # Monday
    ]
    assert result == expected


def test_generate_duplication_dates_unsorted_weekdays():
    """Test that unsorted weekdays are handled correctly"""
    source_date = date(2025, 12, 8)  # Monday
    end_date = date(2025, 12, 22)
    weekdays = [5, 1, 3]  # Saturday, Tuesday, Thursday (unsorted)

    result = generate_duplication_dates(source_date, weekdays, end_date)

    # Result should be sorted
    expected = [
        date(2025, 12, 9),  # Tuesday
        date(2025, 12, 11),  # Thursday
        date(2025, 12, 13),  # Saturday
        date(2025, 12, 16),  # Tuesday
        date(2025, 12, 18),  # Thursday
        date(2025, 12, 20),  # Saturday
    ]
    assert result == expected
    assert result == sorted(result)


def test_generate_duplication_dates_empty_weekdays():
    """Test with empty weekdays list"""
    source_date = date(2025, 12, 8)
    end_date = date(2025, 12, 22)
    weekdays = []

    result = generate_duplication_dates(source_date, weekdays, end_date)

    assert result == []


def test_generate_duplication_dates_short_range():
    """Test with a short date range"""
    source_date = date(2025, 12, 8)  # Monday
    end_date = date(2025, 12, 10)  # Wednesday
    weekdays = [1, 3, 5]  # Tuesday, Thursday, Saturday

    result = generate_duplication_dates(source_date, weekdays, end_date)

    # Only Tuesday falls in range
    expected = [date(2025, 12, 9)]  # Tuesday
    assert result == expected


def test_generate_duplication_dates_exact_end_date():
    """Test when a weekday falls exactly on end_date"""
    source_date = date(2025, 12, 8)  # Monday
    end_date = date(2025, 12, 16)  # Tuesday (exactly)
    weekdays = [1]  # Tuesday

    result = generate_duplication_dates(source_date, weekdays, end_date)

    expected = [
        date(2025, 12, 9),  # Tuesday
        date(2025, 12, 16),  # Tuesday (included)
    ]
    assert result == expected


def test_generate_duplication_dates_no_matching_days():
    """Test when no weekdays fall in the range"""
    source_date = date(2025, 12, 8)  # Monday
    end_date = date(2025, 12, 9)  # Tuesday
    weekdays = [3, 4, 5]  # Thursday, Friday, Saturday

    result = generate_duplication_dates(source_date, weekdays, end_date)

    assert result == []


def test_generate_duplication_dates_same_weekday_as_source():
    """Test when requested weekday is same as source_date weekday"""
    source_date = date(2025, 12, 8)  # Monday (weekday=0)
    end_date = date(2025, 12, 22)
    weekdays = [0]  # Monday

    result = generate_duplication_dates(source_date, weekdays, end_date)

    # Should start from next Monday, not the source_date itself
    expected = [
        date(2025, 12, 15),  # Next Monday
        date(2025, 12, 22),  # Following Monday
    ]
    assert result == expected


def test_generate_duplication_dates_weekday_before_source_in_same_week():
    """Test when requested weekday is before source_date in current week"""
    source_date = date(2025, 12, 11)  # Thursday (weekday=3)
    end_date = date(2025, 12, 25)
    weekdays = [1]  # Tuesday (before Thursday in week)

    result = generate_duplication_dates(source_date, weekdays, end_date)

    # Should go to next week's Tuesday
    expected = [
        date(2025, 12, 16),  # Next Tuesday
        date(2025, 12, 23),  # Following Tuesday
    ]
    assert result == expected


def test_generate_duplication_dates_weekday_after_source_in_same_week():
    """Test when requested weekday is after source_date in current week"""
    source_date = date(2025, 12, 9)  # Tuesday (weekday=1)
    end_date = date(2025, 12, 25)
    weekdays = [4]  # Friday (after Tuesday in week)

    result = generate_duplication_dates(source_date, weekdays, end_date)

    # Should include this week's Friday
    expected = [
        date(2025, 12, 12),  # This Friday
        date(2025, 12, 19),  # Next Friday
    ]
    assert result == expected


def test_generate_duplication_dates_duplicate_weekdays_in_list():
    """Test with duplicate weekdays in the list"""
    source_date = date(2025, 12, 8)  # Monday
    end_date = date(2025, 12, 22)
    weekdays = [1, 1, 3, 3, 1]  # Duplicates

    result = generate_duplication_dates(source_date, weekdays, end_date)

    # Should not create duplicate dates
    expected = [
        date(2025, 12, 9),  # Tuesday
        date(2025, 12, 11),  # Thursday
        date(2025, 12, 16),  # Tuesday
        date(2025, 12, 18),  # Thursday
    ]

    assert result == expected
    # Verify no duplicates in result
    assert len(result) == len(set(result))


def test_generate_duplication_dates_long_range():
    """Test with a longer date range"""
    source_date = date(2025, 1, 1)  # Wednesday
    end_date = date(2025, 3, 31)
    weekdays = [0]  # Monday only

    result = generate_duplication_dates(source_date, weekdays, end_date)

    # Should have ~13 Mondays in 3 months
    assert len(result) == 13
    # Verify all are Mondays
    assert all(d.weekday() == 0 for d in result)
    # Verify they're all in range
    assert all(source_date < d <= end_date for d in result)


def test_generate_duplication_dates_result_is_sorted():
    """Test that result is always sorted regardless of weekday order"""
    source_date = date(2025, 12, 8)
    end_date = date(2025, 12, 31)
    weekdays = [6, 0, 4, 2]  # Random order

    result = generate_duplication_dates(source_date, weekdays, end_date)

    assert result == sorted(result)


@pytest.mark.parametrize(
    "weekdays",
    [[0], [1], [2], [3], [4], [5], [6]],
)
def test_generate_duplication_dates_each_weekday_individually(weekdays):
    """Test each weekday individually"""
    source_date = date(2025, 12, 8)  # Monday
    end_date = date(2025, 12, 31)

    result = generate_duplication_dates(source_date, weekdays, end_date)

    # All dates should have the correct weekday
    assert all(d.weekday() == weekdays[0] for d in result)
    # All dates should be after source_date and <= end_date
    assert all(source_date < d <= end_date for d in result)
    # Dates should be 7 days apart
    for i in range(len(result) - 1):
        assert (result[i + 1] - result[i]).days == 7
