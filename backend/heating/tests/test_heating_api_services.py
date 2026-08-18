from datetime import date, timedelta
from unittest.mock import patch

import pytest

from heating.api.constants import DayStatus
from heating.api.services import (
    add_day_status,
    build_ai_duplication_recap,
    generate_duplication_dates,
    group_slots_hashes_by_date,
    validate_ai_duplication_request,
)
from rooms.tests.factories import RoomFactory

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


# ------------------------------------------------------------------------------
# Tests for error_in_duplication_dates
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


# ------------------------------------------------------------------------------
# Tests for validate_ai_duplication_request
# ------------------------------------------------------------------------------

TODAY = date(2026, 8, 15)
KNOWN_ROOM_IDS = {1, 2, 3, 4}


def test_validate_ai_duplication_request_ok():
    result = validate_ai_duplication_request(
        [1, 2], [0, 2], "2026-08-16", "2026-08-19", KNOWN_ROOM_IDS, TODAY
    )
    assert result["status"] == "ok"
    assert result["message"] == ""
    assert result["nb_days_impacted"] == 2  # Monday 17 + Wednesday 19


def test_validate_ai_duplication_request_warning_above_threshold():
    # every day for 60 days > threshold (30)
    result = validate_ai_duplication_request(
        [1], [0, 1, 2, 3, 4, 5, 6], "2026-08-16", "2026-10-15", KNOWN_ROOM_IDS, TODAY
    )
    assert result["status"] == "warning"
    assert "confirmez-vous" in result["message"]
    assert result["nb_days_impacted"] > 30


def test_validate_ai_duplication_request_start_today_is_allowed():
    # today is not over yet, its plan can still be duplicated onto
    result = validate_ai_duplication_request(
        [1], [TODAY.weekday()], TODAY.isoformat(), TODAY.isoformat(), KNOWN_ROOM_IDS, TODAY
    )
    assert result["status"] == "ok"
    assert result["nb_days_impacted"] == 1


def test_validate_ai_duplication_request_source_date_in_future_start_before_it_is_allowed():
    # start only needs to be >= today, it may be before a future source_date
    result = validate_ai_duplication_request(
        [1], [0], "2026-08-17", "2026-08-17", KNOWN_ROOM_IDS, TODAY
    )
    assert result["status"] == "ok"


@pytest.mark.parametrize(
    "room_ids, weekdays, start, end, expected_message_snippet",
    [
        ([], [0], "2026-08-16", "2026-08-20", "Aucune pièce"),
        ([1, 1], [0], "2026-08-16", "2026-08-20", "pièces sont dupliquées"),
        ([1, 99], [0], "2026-08-16", "2026-08-20", "non proposées"),
        ([1], [], "2026-08-16", "2026-08-20", "Aucun jour"),
        ([1], [0, 0], "2026-08-16", "2026-08-20", "jours de la semaine sont dupliqués"),
        ([1], [7], "2026-08-16", "2026-08-20", "invalide"),
        ([1], [-1], "2026-08-16", "2026-08-20", "invalide"),
        ([1], [0], "not-a-date", "2026-08-20", "début invalide"),
        ([1], [0], "2026-08-16", "not-a-date", "fin invalide"),
        ([1], [0], "2026-08-14", "2026-08-20", "aujourd'hui ou une date future"),
        ([1], [0], "2026-08-20", "2026-08-16", "postérieure ou égale"),
        ([1], [0], "2026-08-16", "2028-08-16", "dépasse le maximum"),
        # start/end range has no Sunday at all
        ([1], [6], "2026-08-17", "2026-08-19", "ne correspond aux jours"),
    ],
)
def test_validate_ai_duplication_request_errors(
    room_ids, weekdays, start, end, expected_message_snippet
):
    result = validate_ai_duplication_request(
        room_ids, weekdays, start, end, KNOWN_ROOM_IDS, TODAY
    )
    assert result["status"] == "error"
    assert result["nb_days_impacted"] == 0
    assert expected_message_snippet in result["message"]


# ------------------------------------------------------------------------------
# Tests for build_ai_duplication_recap
# ------------------------------------------------------------------------------


@pytest.mark.django_db
def test_build_ai_duplication_recap_all_rooms_single_weekday():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre R")
    all_room_ids = {room_a.id, room_b.id}

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),  # Saturday
        [room_a.id, room_b.id],
        [2],  # Wednesday
        date(2026, 8, 16),
        date(2026, 8, 30),
        all_room_ids,
    )

    assert recap == (
        "Je récapitule, vous voulez copier les plannings de toutes les pièces "
        "du samedi 15 août 2026 sur tous les mercredi "
        "entre le mercredi 19 août 2026 et le mercredi 26 août 2026 ?"
    )


@pytest.mark.django_db
def test_build_ai_duplication_recap_single_room_single_weekday():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre R")

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),
        [room_a.id],
        [2],
        date(2026, 8, 16),
        date(2026, 8, 30),
        {room_a.id, room_b.id},
    )

    assert recap == (
        "Je récapitule, vous voulez copier le planning de Chambre P "
        "du samedi 15 août 2026 sur tous les mercredi "
        "entre le mercredi 19 août 2026 et le mercredi 26 août 2026 ?"
    )


@pytest.mark.django_db
def test_build_ai_duplication_recap_two_rooms_two_weekdays():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre d'amis")
    room_c = RoomFactory(name="Cuisine")

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),
        [room_a.id, room_b.id],
        [2, 3],  # Wednesday, Thursday
        date(2026, 8, 16),
        date(2026, 8, 30),
        {room_a.id, room_b.id, room_c.id},
    )

    assert recap == (
        "Je récapitule, vous voulez copier les plannings de Chambre P et Chambre d'amis "
        "du samedi 15 août 2026 sur tous les mercredi et jeudi "
        "entre le mercredi 19 août 2026 et le jeudi 27 août 2026 ?"
    )


@pytest.mark.django_db
def test_build_ai_duplication_recap_three_rooms_three_weekdays():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre R")
    room_c = RoomFactory(name="Chambre M")
    room_d = RoomFactory(name="Cuisine")

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),
        [room_a.id, room_b.id, room_c.id],
        [0, 2, 4],  # Monday, Wednesday, Friday
        date(2026, 8, 16),
        date(2026, 9, 15),
        {room_a.id, room_b.id, room_c.id, room_d.id},
    )

    assert recap.startswith(
        "Je récapitule, vous voulez copier les plannings de Chambre P, Chambre R et Chambre M "
        "du samedi 15 août 2026 sur tous les lundi, mercredi et vendredi "
    )


@pytest.mark.django_db
def test_build_ai_duplication_recap_all_weekdays():
    room_a = RoomFactory(name="Chambre P")
    room_b = RoomFactory(name="Chambre R")

    recap = build_ai_duplication_recap(
        date(2026, 8, 15),
        [room_a.id],
        [0, 1, 2, 3, 4, 5, 6],
        date(2026, 8, 16),
        date(2026, 8, 23),
        {room_a.id, room_b.id},
    )

    assert recap == (
        "Je récapitule, vous voulez copier le planning de Chambre P "
        "du samedi 15 août 2026 sur tous les jours "
        "entre le dimanche 16 août 2026 et le dimanche 23 août 2026 ?"
    )
