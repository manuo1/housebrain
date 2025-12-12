from datetime import date, datetime, timedelta, timezone

import pytest
from core.utils.date_utils import (
    get_week_containing_date,
    is_delta_within_five_seconds,
    is_delta_within_one_minute,
    is_delta_within_two_minute,
    parse_iso_datetime,
    weekdays_str_to_datetime_weekdays,
)
from freezegun import freeze_time


@pytest.mark.parametrize(
    "delta, expected",
    [
        (timedelta(seconds=30), True),  # moins d'une minute
        (timedelta(minutes=1), True),  # exactement une minute
        (timedelta(minutes=1, seconds=1), False),  # plus d'une minute
    ],
)
@freeze_time("2025-10-15 12:00:00+01:00")
def test_is_delta_within_one_minute_param(delta, expected):
    now = datetime.now()
    other_dt = now - delta
    assert is_delta_within_one_minute(now, other_dt) is expected


@pytest.mark.parametrize(
    "delta, expected",
    [
        (timedelta(seconds=30), True),  # moins d'une minute
        (timedelta(minutes=1), True),  # exactement une minute
        (timedelta(minutes=2), True),  # exactement 2 minute
        (timedelta(minutes=2, seconds=1), False),  # plus d'une minute
    ],
)
@freeze_time("2025-10-15 12:00:00+01:00")
def test_is_delta_within_two_minute_param(delta, expected):
    now = datetime.now()
    other_dt = now - delta
    assert is_delta_within_two_minute(now, other_dt) is expected


@pytest.mark.parametrize(
    "dt_str, expected",
    [
        ("2025-10-15T10:55:53.438", datetime(2025, 10, 15, 10, 55, 53, 438000)),
        (
            "2025-10-15T10:55:53.438Z",
            datetime(2025, 10, 15, 10, 55, 53, 438000, tzinfo=timezone.utc),
        ),
        (None, None),
        ("", None),
        ("invalid", None),
        (datetime(2025, 10, 16), None),
        (
            "2025-12-31T23:59:59.999Z",
            datetime(2025, 12, 31, 23, 59, 59, 999000, tzinfo=timezone.utc),
        ),
        ("2025-01-01T00:00:00Z", datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
    ],
)
def test_parse_iso_datetime(dt_str, expected):
    dt = parse_iso_datetime(dt_str)
    if expected is None:
        assert dt is None
    else:
        assert isinstance(dt, datetime)
        assert dt == expected


@pytest.mark.parametrize(
    "delta, expected",
    [
        (timedelta(seconds=10), False),
        (timedelta(seconds=5), True),
        (timedelta(seconds=1), True),
        (timedelta(minutes=1), False),
    ],
)
@freeze_time("2025-10-15 12:00:00+01:00")
def test_is_delta_within_five_seconds(delta, expected):
    now = datetime.now()
    other_dt = now - delta
    assert is_delta_within_five_seconds(now, other_dt) is expected


@pytest.mark.parametrize(
    "label_list, weekday",
    [
        (
            [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
            [0, 1, 2, 3, 4, 5, 6],
        ),
        (["monday"], [0]),
        ("tuesday", None),
        (None, None),
        (False, None),
        ([], []),
        ({}, None),
    ],
)
def test_weekdays_str_to_datetime_weekdays(label_list, weekday):
    assert weekdays_str_to_datetime_weekdays(label_list) == weekday


@pytest.mark.parametrize(
    "input_date,expected_start",
    [
        (date(2025, 1, 15), date(2025, 1, 13)),  # mercredi
        (date(2025, 1, 13), date(2025, 1, 13)),  # lundi
        (date(2025, 1, 19), date(2025, 1, 13)),  # dimanche
        (date(2024, 12, 30), date(2024, 12, 30)),  # autre semaine
    ],
)
def test_get_week_containing_date_valid(input_date, expected_start):
    result = get_week_containing_date(input_date)

    assert len(result) == 7
    assert result[0] == expected_start
    assert result == [expected_start + timedelta(days=i) for i in range(7)]


@pytest.mark.parametrize("input_date", ["a", False, None, {}])
def test_get_week_containing_date_invalid(input_date):
    result = get_week_containing_date(input_date)
    assert result == []
